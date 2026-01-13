FROM python:3.11-slim

ENV ODOO_HOME=/opt/odoo \
    ODOO_USER=odoo

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    node-less \
    npm \
    git \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -d $ODOO_HOME -U -r -s /bin/bash $ODOO_USER

WORKDIR $ODOO_HOME
COPY . $ODOO_HOME
RUN pip install --no-cache-dir -r requirements.txt
RUN chown -R $ODOO_USER:$ODOO_USER $ODOO_HOME

USER $ODOO_USER
EXPOSE 8069

CMD ["python3", "odoo-bin"]
