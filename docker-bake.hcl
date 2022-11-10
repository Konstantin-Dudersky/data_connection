/*
Запустить сборку и загрузку образов:

docker buildx bake --builder builder -f docker-bake.hcl --push kleck
*/

variable "PYTHON_VER" { default = "3.11.0" }
variable "POETRY_VER" { default = "1.2.2" }

# базовый образ для сервисов python
target "data_connection_base" {
    dockerfile = "Dockerfile.base"
    args = {
        POETRY_VER = "${POETRY_VER}",
        PYTHON_VER = "${PYTHON_VER}"
    }
    platforms = [
        "linux/amd64",
    ]
}


target "opcua_client_reader_side" {
    contexts = {
        base = "target:data_connection_base",
    }
    dockerfile = "./test/opcua_client/test_reader_side/Dockerfile"
    tags = [ "target:5000/data_connection/opcua_client_reader_side" ]
    platforms = [
        "linux/amd64",
    ]
}
target "opcua_client_writer_side" {
    contexts = {
        base = "target:data_connection_base",
    }
    dockerfile = "./test/opcua_client/test_writer_side/Dockerfile"
    tags = [ "target:5000/data_connection/opcua_client_writer_side" ]
    platforms = [
        "linux/amd64",
    ]
}
group "opcua_client" {
    targets = [
        "opcua_client_reader_side",
        "opcua_client_writer_side",
    ]
}
