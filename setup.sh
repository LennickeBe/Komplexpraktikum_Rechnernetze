#!/usr/bin/env bash

### Check pip ###

if ! command -v pip &> /dev/null; then
    echo "pip could not be found. Installing...."
    sudo apt install python3-pip
fi


### Check ansible ###

if ! command -v ansible &> /dev/null; then
    echo "ansible could not be found. Installing...."
    sudo apt install ansible
fi


### Install Services ###

DOCKERINSTALLER="#!/usr/bin/env bash
if ! command -v docker &> /dev/null; then 
echo 'Docker could not be found. Installing now!' 
curl -fsSL https://get.docker.com/ -o get-docker.sh 
sudo sh get-docker.sh
fi"

echo "Installing services now..."
for service in PUSHGATEWAY PROMETHEUS GRAFANA
do
    echo "Installing ${service}... "
    read -p "Target IP of ${service} node: " service_IP
    read -p "Username for that remote node: " USERNAME

        case $service in
            "PUSHGATEWAY")
                echo "Installing gateway docker image..."
                ssh -t -l ${USERNAME} ${service_IP} "eval ${DOCKERINSTALLER}; sudo docker run -d -p 9091:9091 --name pushgateway prom/pushgateway"
                sed -i "s/PLACEHOLDER_GATEWAY_IP/${service_IP}:9091/" ./configs/prometheus/prometheus.yml
                sed -i "s/PLACEHOLDER_GATEWAY_IP/${service_IP}/" ./configs/setup.yml
                ;;
            "PROMETHEUS")
                PROM_IP=$service_IP
                echo "Making config directory now..."
                ssh -t -l ${USERNAME} ${service_IP} "mkdir -p ~/configs/prometheus/"
                echo "Copying prometheus config into remote node..."
                scp ./configs/prometheus/prometheus.yml ${USERNAME}@${service_IP}:~/configs/prometheus/prometheus.yml
                echo "Installing prometheus docker image..."
                ssh -t -l ${USERNAME} ${service_IP} "eval ${DOCKERINSTALLER}; sudo docker run -d --name=prometheus -p 9090:9090 --mount type=bind,source=/home/${USERNAME}/configs/prometheus/prometheus.yml,target=/etc/prometheus/prometheus.yml prom/prometheus:latest --config.file=/etc/prometheus/prometheus.yml"
                sed -i "s/PLACEHOLDER_PROMETHEUS_IP/${service_IP}:9091/" ./configs/setup.yml
                ;;
            "GRAFANA")
                echo "Making config directory now..."
                ssh -t -l ${USERNAME} ${service_IP} "mkdir -p ~/configs/grafana/"
                echo "Copying grafana config into remote node..."
                scp ./configs/grafana/datasources.yml ${USERNAME}@${service_IP}:~/configs/grafana/datasources.yml
                echo "Installing grafana docker image..."
                ssh -t -l ${USERNAME} ${service_IP} "eval ${DOCKERINSTALLER}; sudo docker run -d --name=grafana -p 3000:3000 -e PROM_IP=${PROM_IP} --mount type=bind,source=/home/${USERNAME}/configs/grafana/datasources.yml,target=/etc/grafana/provisioning/datasources/datasource.yml grafana/grafana:latest"
                sed -i "s/PLACEHOLDER_GRAFANA_IP/${service_IP}:9091/" ./configs/setup.yml
                ;;
        esac
done

### Read ssh key location ###

read -p "Location of SSH key to target hosts (usually under ~/.ssh/): " ssh_key

### Run ansible playbook ###

ansible-playbook playbook.yml -i inventory.yml --private-key=${ssh_key}