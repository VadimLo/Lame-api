# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /code


COPY requirements.txt /code
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP main_app.py
ENV FLASK_DEBUG 1

CMD ["gunicorn", "main_app:app", "-b", "0.0.0.0:8000"]

#ENTRYPOINT ["python3"]
#CMD ["main_app.py"]

FROM builder as dev-envs



#RUN <<EOF
#apk update
#apk add git
#EOF
#
#RUN <<EOF
#addgroup -S docker
#adduser -S --shell /bin/bash --ingroup docker vscode
#EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

#CMD ["flask", "run"]