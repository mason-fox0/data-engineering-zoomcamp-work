FROM postgres:13

#figure out how to do this securely later
ENV POSTGRES_USER="taxi"
ENV POSTGRES_PASSWORD="pass"
ENV POSTGRES_DB="NYC_Taxi"

WORKDIR /taxi

#mount taxi data folder
RUN mkdir -p /taxi/data

# Setup an app user so the container doesn't run as the root user
RUN useradd -u 9985 -m taxi && chown -R taxi:taxi /taxi/data
USER taxi

#open postgres port
EXPOSE 5432

ENTRYPOINT ["bash"]
