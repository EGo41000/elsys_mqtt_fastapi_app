# elsys_mqtt_fastapi_app
App pour récup par MQTT, affichage graph

```bash
 python3 -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
```

```bash
 source venv/bin/activate
 uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

sudo kubectl create secret generic elsys-env --namespace=elsys --from-env-file=.env.elsys

sudo kubectl get all -o wide -n elsys

sudo kubectl apply -f elsys-deployment.yaml
sudo kubectl rollout restart deployment/elsys-devel -n elsys

sudo kubectl logs deployment.apps/elsys-devel -n elsys
