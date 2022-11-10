FROM base
# контекст - корневая папка репозитория
COPY . /root/code
WORKDIR /root/code/test/opcua_client/test_reader_side
RUN poetry install --only main
RUN rm -rf /root/code
CMD ["poetry", "run", "start"]
# CMD ["tail", "-f", "/dev/null"]
EXPOSE 8000
