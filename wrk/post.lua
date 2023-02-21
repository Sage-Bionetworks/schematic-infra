-- example HTTP POST script which demonstrates setting the
-- HTTP method, body, and adding a header

-- wrk.method = "POST"
-- local f = io.open("/Users/lpeng/Documents/schematic-infra/schematic-infra/test-manifests/synapse_storage_manifest_patient.csv", "rb")
-- wrk.body = f:read("*all")
-- wrk.headers["Content-Type"] = "multipart/form-data"


function read_file(path)
    local file, errorMessage = io.open(path, "rb")
    if not file then
        error("Could not read the file:" .. errorMessage .. "\n")
    end
  
    local content = file:read "*all"
    file:close()
    return content
end


local FileBody = read_file("/Users/lpeng/Downloads/synapse-storage-manifest-big.csv")
local Filename = "synapse-storage-manifest-big.csv"
local ContentDisposition = 'Content-Disposition: form-data; filename="' .. Filename .. '";type=text/csv'
local ContentType = 'Content-Type: multipart/form-data'


wrk.method = "POST"
wrk.headers["Content-Type"] = "multipart/form-data"
wrk.body = ContentDisposition .. ContentType .. FileBody

