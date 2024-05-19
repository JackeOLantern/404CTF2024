import requests as rq
import numpy as np
import perceval as pcvl
import math
from perceval import pdisplay, PS, BS, Circuit, BasicState, Processor, StateVector
from perceval.backends import BackendFactory
from perceval.algorithm import Analyzer
from exqalibur import FockState
from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
from numpy import pi, cos, sin
from typing import Optional, List, Tuple

def ry(theta):
    return np.array([
        [np.cos(theta/2), -np.sin(theta/2)],
        [np.sin(theta/2), np.cos(theta/2)]
    ])

def circuit_to_list(circuit: Circuit) -> List[List[Tuple[float, float]]]:
    return [[(x.real, x.imag) for x in l] for l in np.array(circuit.compute_unitary())]
    
def state_vector_to_list(sv: StateVector) -> List[Tuple[float, float]]:
    if type(sv) is not StateVector:
        sv = pcvl.StateVector(sv)
    sv.normalize()
    r = [(0., 0.), (0., 0.)]
    for k, v in sv:
        r[int(qubits_[k])] = (v.real, v.imag)
    return r

def list_to_state_vector(p: List[Tuple[float, float]]) -> StateVector:
    return complex(p[0][0], p[0][1]) * StateVector([1, 0]) + complex(p[1][0], p[1][1]) * StateVector([0, 1]) 

# Rotations
x_rot = lambda x: Circuit(2) // (0, PS(pi)) // BS.Rx(theta=x) // (0, PS(pi)) 
y_rot = lambda x: BS.Ry(theta=x)
z_rot = lambda x: BS.H() // x_rot(x) // BS.H() 

qubits = {
    "0": BasicState([1, 0]),
    "1": BasicState([0, 1])
}
qubits_ = {qubits[k]: k for k in qubits}
sqlist = [qubits["0"], qubits["1"]]
   

print("\nMesure de EVE\n")
# Define the rotation matrix for Y-axis rotation by pi/8
theta = -np.pi / 50

base_p = y_rot(theta)
base_x = y_rot(-pi/2+theta)

# Rotation matrix for Y-axis by theta
rotation_matrix = ry(theta)

#state_vector = np.array([1, 0])
a0 = [1, 0]
a1 = [0, 1]
r0 = np.dot(rotation_matrix, a0)
r1 = np.dot(rotation_matrix, a1)

qubits_eve = {}
qubits_eve["0"]= math.sqrt(r0[0]) * pcvl.StateVector("|1,0>") - math.sqrt(-1 * r0[1])*pcvl.StateVector("|0,1>") 
qubits_eve["1"]= math.sqrt(r1[0]) * pcvl.StateVector("|1,0>") + math.sqrt(r1[1])*pcvl.StateVector("|0,1>") 

qubits_eve["0x"] = qubits_eve["0"] + qubits_eve["1"] 
qubits_eve["1x"] = qubits_eve["1"] - qubits_eve["0"]

print(qubits_eve)
print(type(qubits_eve["0"]), type(qubits_eve["1"]))
d = {
    "base_eve_1": circuit_to_list(base_p),
    "base_eve_2": circuit_to_list(base_x),
    "qubit_eve_1": state_vector_to_list(qubits_eve["0"]),
    "qubit_eve_2": state_vector_to_list(qubits_eve["1"]),
    "qubit_eve_3": state_vector_to_list(qubits_eve["0x"]),
    "qubit_eve_4": state_vector_to_list(qubits_eve["1x"])
}
print("d:\n", d)


URL = "https://perceval.challenges.404ctf.fr"
print(rq.get(URL + "/healthcheck").json())
print(rq.post(URL + "/challenges/2", json=d).json())