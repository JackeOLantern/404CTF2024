import math
import numpy as np
import perceval as pcvl
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

# On reprend notre encodage par rail
qubits = {
    "0": BasicState([1, 0]),
    "1": BasicState([0, 1])
}
qubits_ = {qubits[k]: k for k in qubits}
sqlist = [qubits["0"], qubits["1"]]
   
# Analyse du circuit
def analyze(circuit: Circuit, input_states: Optional[FockState] = None, output_states: Optional[FockState] = None) \
        -> None:
    if input_states is None:
        input_states = sqlist
    if output_states is None:
        output_states = sqlist
    p = Processor("Naive", circuit)
    a = Analyzer(p, input_states, output_states, mapping=qubits_)
    pdisplay(a)

# Analyse du circuit en calculant les amplitudes
def amplitudes(circuit: Circuit, input_state: Optional[FockState] = None, output_states: Optional[FockState] = None) \
        -> (complex, complex):
    if input_state is None:
        input_state = qubits["0"]
    if output_states is None:
        output_states = sqlist
    b = BackendFactory.get_backend("Naive")
    b.set_circuit(circuit)
    b.set_input_state(input_state)
    return {qubits_[k]: roundc(b.prob_amplitude(k)) for k in output_states}

# Rotations
x_rot = lambda x: Circuit(2) // (0, PS(pi)) // BS.Rx(theta=x) // (0, PS(pi)) 
y_rot = lambda x: BS.Ry(theta=x)
z_rot = lambda x: BS.H() // x_rot(x) // BS.H() 

# Trigonométrie avec Matplotlib 
def plot_trig(angles, colors=None, annotations=None):
    r = 1.5
    if colors is None:
        colors = ["blue"] * len(angles)
    if annotations is None:
        annotations = [""] * len(angles)
    for angle, color, annotation in zip(angles, colors, annotations):
        pos_x = r * cos(angle)
        pos_y = r * sin(angle)
        plt.plot([0, pos_x], [0, pos_y], color=color)
        pos_x_a = pos_x + np.sign(pos_x) * 0.1 - (0.05 * len(annotation) if np.sign(pos_x) < 0 else 0)
        pos_y_a = pos_y + np.sign(pos_y) * 0.1
        plt.gca().annotate(annotation, xy=(pos_x_a, pos_y_a), xycoords='data', fontsize=10)

    plt.plot(0, 0, color='black', marker='o')
    a = np.linspace(0 * pi, 2 * pi, 100)
    xs, ys = r * cos(a), r * sin(a)
    plt.plot(xs, ys, color="black")
    plt.xlim(-2, 2)
    plt.ylim(-2, 2)
    plt.gca().set_aspect('equal')
    plt.show()

# Version de `round()` pour les nombres complexes.
def roundc(c: complex, decimals: int = 2) -> complex:
    return round(c.real, decimals) + round(c.imag, decimals) * 1j


def measure(input_state, circuit, full=False):
    p = pcvl.Processor("SLOS", circuit)
    p.with_input(input_state)
    sampler = pcvl.algorithm.Sampler(p)

    # Mesure (complète) faite avec 1000 essais, on se retrouve donc avec un résultat semblable 
    # à l'Analyser
    if full:
        sample_count = sampler.sample_count(1000)
        return sample_count['results']
        
    sample_count = sampler.sample_count(1)
    return list(sample_count['results'].keys())[0]

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

hadamard_gate = BS.H()
print(amplitudes(hadamard_gate))
analyze(hadamard_gate)
#plot_bloch(hadamard_gate)
#pcvl.pdisplay(hadamard_gate)

#plot_trig([0, pi/2, pi/4, -pi/4], ["blue", "blue", "red", "red"], ["|0>", "|1>", "|+>", "|->"])
N = 100
bits_alice = np.random.randint(low=0, high=2, size=(4 * N,))
#plot_trig([0, pi/2, pi/4, 3*pi/4], ["blue", "blue", "red", "red"], ["0 (+)", "1 (+)", "0 (x)", "1 (x)"])
bases_alice = np.array(["+" if b == 0 else "x" for b in np.random.randint(low=0, high=2, size=(4 * N,))])
print(bits_alice)
print(bases_alice)
# ALICE ****
qubits_alice = []

# Pour pouvoir tester plus facilement, je définis les valeurs de 0 et de 1 dans la base X, attention, ce 
# ne sont plus des BasicState, mais des StateVector, il faut donc utiliser la fonction measure (voir
# ci-dessous) pour les manipuler
qubits["0x"] = qubits["0"] + qubits["1"] 
qubits["1x"] = qubits["1"] - qubits["0"] 
print(type(qubits["0"]), type(qubits["0x"]))

for bit, basis  in zip(bits_alice, bases_alice):
    if basis == "+":
        s = pcvl.StateVector(qubits["0"]) if bit == 0 else pcvl.StateVector(qubits["1"])
    else: 
        s = qubits["0x"] if bit == 0 else qubits["1x"]
    qubits_alice.append(s)

    # On affiche les 9 premiers pour vérifier :
    #if len(qubits_alice) < 10: from perceval.lib import Gate
    #    print(f"Bit à encoder : {bit}, base choisie : {basis}, qubit correspondant : {s}")

# EVE ****
#plot_trig([0, pi/2, pi/4, -pi/4], ["blue", "blue", "red", "red"], ["|0>", "|1>", "|+>", "|->"])
print("\nMesure de EVE\n")
bases_eve = np.array(["+" if b == 0 else "x" for b in np.random.randint(low=0, high=2, size=(4 * N,))])

# Define the rotation matrix for Y-axis rotation by pi/8
base_p = Circuit(2)
base_x = y_rot(-pi/2)
print('before :\n', circuit_to_list(base_p),"\n", circuit_to_list(base_x))
theta = - np.pi /50
base_p = y_rot(theta)
base_x = y_rot(-pi/2+theta)
print('after eve :\n', circuit_to_list(base_p),"\n", circuit_to_list(base_x))

# Rotation matrix for Y-axis by theta
rotation_matrix = ry(theta)

a0 = [1, 0]
a1 = [0, 1]
r0 = np.dot(rotation_matrix, a0)
r1 = np.dot(rotation_matrix, a1)
qubitsE={}
#qubitsE["0"] = (1 / math.sqrt(2)) * qubits["0"]+(1 / math.sqrt(2)) *qubits["0x"]
#qubitsE["1"] = (1 / math.sqrt(2)) *qubits["1"]+(1 / math.sqrt(2)) *qubits["1x"]
#print(qubitsE)
qubitsE["0"]= math.sqrt(r0[0])*pcvl.StateVector("|1,0>") - math.sqrt(-1 * r0[1])*pcvl.StateVector("|0,1>") 
qubitsE["1"]= math.sqrt(r1[0]) * pcvl.StateVector("|1,0>") + math.sqrt(r1[1])*pcvl.StateVector("|0,1>") 
qubitsE["0x"] = qubitsE["0"] + qubitsE["1"] 
qubitsE["1x"] = qubitsE["1"] - qubitsE["0"]

print(qubitsE)
print(type(qubitsE["0"]), type(qubitsE["1"]))

print(f"""
0 dans la baseE + : {measure(qubitsE["0"], base_p, full=True)}
1 dans la baseE + : {measure(qubitsE["1"], base_p, full=True)}
0 dans la baseE x ({qubitsE["0x"]}) mesurée dans la base + : {measure(qubitsE["0x"], base_p, full=True)}
1 dans la baseE x ({qubitsE["1x"]}) mesurée dans la base + : {measure(qubitsE["1x"], base_p, full=True)}
""")

print("\nRotate y: ", theta," \n")

print(f"""
0 dans la baseE x : {measure(qubitsE["0x"], base_x, full=True)}
1 dans la baseE x : {measure(qubitsE["1x"], base_x, full=True)}
0 dans la baseE + ({qubitsE["0"]}) mesurée dans la base x : {measure(qubitsE["0"], base_x, full=True)}
1 dans la baseE + ({qubitsE["1"]}) mesurée dans la base x : {measure(qubitsE["1"], base_x, full=True)}
""")
'''
d = {
    "base_eve_1": circuit_to_list(base_p),
    "base_eve_2": circuit_to_list(base_x),
    "qubit_eve_1": state_vector_to_list(qubits_eve["0"]),
    "qubit_eve_2": state_vector_to_list(qubits_eve["1"]),
    "qubit_eve_3": state_vector_to_list(qubits_eve["0x"]),
    "qubit_eve_4": state_vector_to_list(qubits_eve["1x"])
}
print("d:\n", d)
'''

bits_eve = []
for q, b in zip(qubits_alice, bases_eve): 
    if b == "+":
        bits_eve.append(0 if measure(q, base_p) == qubits["0"] else 1)
    else:
        bits_eve.append(0 if measure(q, base_x) == qubits["0"] else 1)
bits_eve = np.array(bits_eve)
#print(bits_eve)
#print(bases_eve)

correspondance_secret_key_bits_eve = bits_eve == bits_alice
corr = np.sum(correspondance_secret_key_bits_eve) / (4 * N)

#print("Corr list :", correspondance_secret_key_bits_eve)
print("Corr average : EVE", corr)

qubits_eve = []

for bit, basis  in zip(bits_eve, bases_eve):
    if basis == "+":
        s = pcvl.StateVector(qubits["0"]) if bit == 0 else pcvl.StateVector(qubits["1"])
    else: 
        s = qubits["0x"] if bit == 0 else qubits["1x"]
    qubits_eve.append(s)

print("\nMesure de BOB\n")
bases_bob = np.array(["+" if b == 0 else "x" for b in np.random.randint(low=0, high=2, size=(4*N,))])
base_p = Circuit(2)
base_x = y_rot(-pi/2)

bits_bob = []
for q, b in zip(qubits_eve, bases_bob): 
    if b == "+":
        bits_bob.append(0 if measure(q, base_p) == qubits["0"] else 1)
    else:
        bits_bob.append(0 if measure(q, base_x) == qubits["0"] else 1)
bits_bob = np.array(bits_bob)
print(bases_bob)
print(bits_bob)

correspondance_secret_key_bits_bob_eve = bits_bob == bits_eve
corrEve = np.sum(correspondance_secret_key_bits_bob_eve) / (4 * N)

correspondance_secret_key_bits_bob = bits_bob == bits_alice
corr = np.sum(correspondance_secret_key_bits_bob) / (4 * N)

#print("Corr list :", correspondance_secret_key_bits_bob)
print("Corr average EVE :", corrEve)
print("Corr average ALICE :", corr)
# PUBLICATION ALICE de ses bases

print("\nAlice publie ses bases :\n")

correspondance_bases_alice_bob = bases_bob == bases_alice
print("correspondance_bases_alice_bob :", correspondance_bases_alice_bob)
half_bits_bob = bits_bob[correspondance_bases_alice_bob]
half_bits_alice = bits_alice[correspondance_bases_alice_bob]
print("bits_bob :", bits_bob)
print("half_bits_bob :", half_bits_bob)
print("bits_alice :", bits_alice)
print("half_bits_alice :", half_bits_alice)

# ATTENTION : Ne pas relancer la cellule toute seule, relancer tout le notebook pour rafraichir cette cellule correctement. 

last_slice = len(half_bits_bob) // 2
verification = half_bits_bob[:last_slice] == half_bits_alice[:last_slice]
print(f"Pourcentage de correspondance : {int(np.sum(verification) / last_slice * 100)}%")

secret_key = half_bits_bob[last_slice:]
print(f"Secret key : {secret_key}, taille : {len(secret_key)}")
