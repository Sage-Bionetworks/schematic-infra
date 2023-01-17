import subprocess
import sys

# -c, --connections <N>  Connections to keep open
# -d, --duration    <T>  Duration of test
# -t, --threads     <N>  Number of threads to use

# -s, --script      <S>  Load Lua script file
# -H, --header      <H>  Add header to request
#     --latency          Print latency statistics
#     --timeout     <T>  Socket/request timeout
# -v, --version          Print version details


# subprocess

result_one = subprocess.run(
    [
        "wrk",
        "-c1",
        "-d30",
        "-t1",
        "--latency",
        "https://schematic.dnt-dev.sagebase.org/v1/explorer/get_node_dependencies?schema_url=https%3A%2F%2Fraw.githubusercontent.com%2FSage-Bionetworks%2Fschematic%2Fdevelop%2Ftests%2Fdata%2Fexample.model.jsonld&source_node=Patient&return_display_names=true&return_schema_ordered=true",
    ],
    stdout=subprocess.PIPE,
)


result_two = subprocess.run(
    [
        "wrk",
        "-c5",
        "-d30",
        "-t1",
        "--latency",
        "https://schematic.dnt-dev.sagebase.org/v1/explorer/get_node_dependencies?schema_url=https%3A%2F%2Fraw.githubusercontent.com%2FSage-Bionetworks%2Fschematic%2Fdevelop%2Ftests%2Fdata%2Fexample.model.jsonld&source_node=Patient&return_display_names=true&return_schema_ordered=true",
    ],
    stdout=subprocess.PIPE,
)


result_three = subprocess.run(
    [
        "wrk",
        "-c10",
        "-d30",
        "-t1",
        "--latency",
        "https://schematic.dnt-dev.sagebase.org/v1/explorer/get_node_dependencies?schema_url=https%3A%2F%2Fraw.githubusercontent.com%2FSage-Bionetworks%2Fschematic%2Fdevelop%2Ftests%2Fdata%2Fexample.model.jsonld&source_node=Patient&return_display_names=true&return_schema_ordered=true",
    ],
    stdout=subprocess.PIPE,
)

result_four = subprocess.run(
    [
        "wrk",
        "-c20",
        "-d30",
        "-t1",
        "--latency",
        "https://schematic.dnt-dev.sagebase.org/v1/explorer/get_node_dependencies?schema_url=https%3A%2F%2Fraw.githubusercontent.com%2FSage-Bionetworks%2Fschematic%2Fdevelop%2Ftests%2Fdata%2Fexample.model.jsonld&source_node=Patient&return_display_names=true&return_schema_ordered=true",
    ],
    stdout=subprocess.PIPE,
)


result_five = subprocess.run(
    [
        "wrk",
        "-c40",
        "-d30",
        "--timeout",
        "100s",
        "-t1",
        "--latency",
        "https://schematic.dnt-dev.sagebase.org/v1/explorer/get_node_dependencies?schema_url=https%3A%2F%2Fraw.githubusercontent.com%2FSage-Bionetworks%2Fschematic%2Fdevelop%2Ftests%2Fdata%2Fexample.model.jsonld&source_node=Patient&return_display_names=true&return_schema_ordered=true",
    ],
    stdout=subprocess.PIPE,
)

with open("get-node-dependencies.txt", "w") as writer:
    writer.write(result_one.stdout.decode("utf-8"))
    writer.write("\n")
    writer.write(result_two.stdout.decode("utf-8"))
    writer.write("\n")
    writer.write(result_three.stdout.decode("utf-8"))
    writer.write("\n")
    writer.write(result_four.stdout.decode("utf-8"))
    writer.write("\n")
    writer.write(result_five.stdout.decode("utf-8"))
