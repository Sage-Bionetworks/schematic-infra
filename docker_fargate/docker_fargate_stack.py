from aws_cdk import (Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as r53,
    CfnOutput,
    Duration,
    Tags)

import config as config
import aws_cdk.aws_certificatemanager as cm
import aws_cdk.aws_secretsmanager as sm
from constructs import Construct

ACM_CERT_ARN_CONTEXT = "ACM_CERT_ARN"
IMAGE_PATH_AND_TAG_CONTEXT = "IMAGE_PATH_AND_TAG"
PORT_NUMBER_CONTEXT = "PORT"

# The name of the environment variable that will hold the secrets
SECRETS_MANAGER_ENV_NAME = "SECRETS_MANAGER_SECRETS"
CONTAINER_ENV = "CONTAINER_ENV" # name of env passed from GitHub action
ENV_NAME = "ENV"

def get_secret(scope: Construct, id: str, name: str) -> str:
    isecret = sm.Secret.from_secret_name_v2(scope, id, name)
    return ecs.Secret.from_secrets_manager(isecret)
    # see also: https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_ecs/Secret.html
    # see also: ecs.Secret.from_ssm_parameter(ssm.IParameter(parameter_name=name))

def get_container_env(env: dict) -> str:
    return env.get(CONTAINER_ENV)

def get_certificate_arn(env: dict) -> str:
    return env.get(ACM_CERT_ARN_CONTEXT)

def get_docker_image_name(env: dict):
    return env.get(IMAGE_PATH_AND_TAG_CONTEXT)

def get_port(env: dict) -> int:
    return int(env.get(PORT_NUMBER_CONTEXT))


class DockerFargateStack(Stack):

    def __init__(self, scope: Construct, context: str, env: dict, vpc: ec2.Vpc, **kwargs) -> None:
        stack_prefix = f'{env.get(config.STACK_NAME_PREFIX_CONTEXT)}-{context}'
        stack_id = f'{stack_prefix}-DockerFargateStack'
        super().__init__(scope, stack_id, **kwargs)

        cluster = ecs.Cluster(
            self,
            f'{stack_prefix}-Cluster',
            vpc=vpc,
            container_insights=True)

        secret_name = f'{stack_id}/{context}/ecs'
        secrets = {
            SECRETS_MANAGER_ENV_NAME: get_secret(self, secret_name, secret_name)
        }

        env_vars = {}
        container_env = get_container_env(env)
        if container_env is not None:
            env_vars[ENV_NAME]=container_env

        task_image_options = ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                   image=ecs.ContainerImage.from_registry(get_docker_image_name(env)),
                   environment=env_vars,
                   secrets = secrets,
                   container_port = get_port(env))

        cert = cm.Certificate.from_certificate_arn(
            self,
            f'{stack_id}-Certificate',
            get_certificate_arn(env),
        )

        #
        # for options to pass to ApplicationLoadBalancedTaskImageOptions see:
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedTaskImageOptions.html#aws_cdk.aws_ecs_patterns.ApplicationLoadBalancedTaskImageOptions
        # Documentation on CPU and memory size: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definition_parameters.html
        load_balanced_fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            f'{stack_prefix}-Service',
            cluster=cluster,            # Required
            cpu=4096,                    # Default is 256 which is 0.25vCPU; 4096 is 4 vCPU
            desired_count=3,            # Number of copies of the 'task' (i.e. the app') running behind the ALB
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True), # Enable rollback on deployment failure
            task_image_options=task_image_options,
            memory_limit_mib=8192,      # Default is 512; 8192 MiB is equivalent to 8GB.
            public_load_balancer=True,  # Default is False
            idle_timeout=Duration.seconds(300), # Modify default idle time out to avoid 504 gateway error
            # TLS:
            certificate=cert,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            target_protocol=elbv2.ApplicationProtocol.HTTPS,
            ssl_policy=elbv2.SslPolicy.FORWARD_SECRECY_TLS12_RES, # Strong forward secrecy ciphers and TLS1.2 only.
        )

        # Overriding health check timeout helps with sluggishly responding app's (e.g. Shiny)
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationTargetGroup.html#aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup

        # The number of consecutive health check failures required before considering a target unhealthy. For Application Load Balancers, the default is 2.
        #
        load_balanced_fargate_service.target_group.configure_health_check(protocol=elbv2.Protocol.HTTPS, interval=Duration.seconds(120), timeout=Duration.seconds(60), path="/v1/ui/", healthy_http_codes="200-308", unhealthy_threshold_count=5)

        if True: # enable/disable autoscaling
            scalable_target = load_balanced_fargate_service.service.auto_scale_task_count(
               min_capacity=3, # Minimum capacity to scale to. Default: 1
               max_capacity=5 # Maximum capacity to scale to.
            )

            # Add more capacity when CPU utilization reaches 50%
            scalable_target.scale_on_cpu_utilization("CpuScaling",
                target_utilization_percent=50
            )

            # Add more capacity when memory utilization reaches 50%
            scalable_target.scale_on_memory_utilization("MemoryScaling",
                target_utilization_percent=50
            )

            # Other metrics to drive scaling are discussed here:
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_autoscaling/README.html

        # Tag all resources in this Stack's scope with context tags
        for key, value in env.get(config.TAGS_CONTEXT).items():
            Tags.of(scope).add(key, value)

        # Export load balancer name
        lb_dns_name = load_balanced_fargate_service.load_balancer.load_balancer_dns_name
        lb_dns_export_name = f'{stack_id}-LoadBalancerDNS'
        CfnOutput(self, 'LoadBalancerDNS', value=lb_dns_name, export_name=lb_dns_export_name)
