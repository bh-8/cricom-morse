FROM debian AS cricom
    RUN apt-get update && apt-get install -y \
        python3 \
        python3-pip \
        python3-venv
    RUN python3 -m venv /home/cricom/venv
    RUN . /home/cricom/venv/bin/activate && pip3 install \
        numpy \
        scipy \
        && deactivate

    # create entrypoint
    RUN echo "#!/bin/bash">/home/entrypoint.sh
    RUN echo ". /home/cricom/venv/bin/activate">>/home/entrypoint.sh
    RUN echo "python3 -u /home/cricom/cricom.py \"\$@\"">>/home/entrypoint.sh
    RUN echo "err_level=\$?">>/home/entrypoint.sh
    RUN echo "deactivate">>/home/entrypoint.sh
    RUN echo "exit \$err_level">>/home/entrypoint.sh
    RUN chmod +x /home/entrypoint.sh

    WORKDIR /home/cricom
    COPY ./src /home/cricom/
    ENTRYPOINT [ "/home/entrypoint.sh" ]
