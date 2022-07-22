"""
This class holds given measurements initialized by the modules to deliver their value to the Pushgateway.
"""
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

class Exporter(object):

    registry = CollectorRegistry()
    measurements = []

    """The class is being initialized as a singleton to prevent the creation of more than one registry."""
    def __new__(cls, gateway_url, instance, module, args):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Exporter, cls).__new__(cls)
        return cls.instance

    def __init__(self, gateway_url, instance, module, args):
        print("intialize Exporter")
        self.gateway_url = gateway_url
        self.instance = instance
        self.module = module
        self.args = args

    def pushToGate(self):
        print(self.gateway_url)
        g_key=dict([("module",self.module),("instance",self.instance)])
        push_to_gateway(gateway=self.gateway_url, job='gateway', grouping_key=g_key, registry=self.registry)
        return print('Sent to gateway')

    def initializeMeasurement(self, title, desc, labels):
        g = Gauge(name=title,documentation=desc, labelnames=['module', 'instance'] + labels, registry=self.registry)
        self.measurements.append(g)
        return g

    def setMeasurement(self, title, value, labelvalues):
        for measurement in self.measurements:
            if str(measurement) == 'gauge:'+title:
                measurement.labels(module=title, instance=self.instance, **labelvalues).set(value)
                self.pushToGate()

