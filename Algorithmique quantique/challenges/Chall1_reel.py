import requests as rq
import numpy as np
import perceval as pcvl
import math

def circuit_to_list(circuit):
    return [[(x.real, x.imag) for x in l] for l in np.array(circuit.compute_unitary())]

# init
qubits = {
    "0": pcvl.BasicState([1, 0]),
    "1": pcvl.BasicState([0, 1])
}
# Dictionnaire (inverse de qubit défini au dessus) servant à afficher directement les qubits lorsqu'on
# utilise des fonctions comme l'ananlyseur. 
qubits_ = {qubits[k]: k for k in qubits}

#STEP 1  Beam splitter
print("STEP 1  Beam splitter\n")
# On peut définir des variables symboliques : 
symbolic_alpha = pcvl.P('α')
step_one = pcvl.BS(theta=symbolic_alpha)

# pour 0.9
x = 2 * math.asin(math.sqrt(0.9))
step_one.assign({'α': x})

p_step_one = pcvl.Processor("Naive", step_one)
a_step_one = pcvl.algorithm.Analyzer(
    p_step_one, 
    input_states=[qubits["0"]], 
    output_states=list(qubits.values()),             
    mapping=qubits_
)

print("L'analyser doit renvoyer : 1/10 pour 0 et 9/10 pour 1")
pcvl.pdisplay(a_step_one)
assert np.isclose(a_step_one.distribution[0][1].real, 0.9)

# Step 2
print("\nSTEP 2\n")
symbolic_beta = pcvl.P("β")
symbolic_gamma = pcvl.P("γ")
step_two = pcvl.BS(theta=symbolic_beta) // (1, pcvl.PS(phi=symbolic_gamma))

beta = 2 * math.acos(np.sqrt(3) / 2)
gamma = 4*np.pi/3
step_two.assign({"β": beta, "γ": gamma})

b_step_two = pcvl.BackendFactory.get_backend("Naive")
b_step_two.set_circuit(step_two)
b_step_two.set_input_state(qubits["0"])

ampl0, ampl1 = b_step_two.prob_amplitude(qubits["0"]), b_step_two.prob_amplitude(qubits["1"])

res = f"|φ> = {np.round(ampl0, 2)} |0> + {np.round(ampl1, 2)} |1>"
sol = f"|φ> = {np.round(np.sqrt(3) / 2 + 0j, 2)} |0> + {np.round(np.sqrt(3) / 4 - 1j / 4, 2)} |1>"

print(f"Résultat : {res}")
print(f"Solution : {sol}")

# Step final
print("\nSTEP final\n")
x_rot = lambda x: pcvl.Circuit(2) // (0, pcvl.PS(np.pi)) // pcvl.BS.Rx(theta=x) // (0, pcvl.PS(np.pi)) 
y_rot = lambda x: pcvl.BS.Ry(theta=x)
z_rot = lambda x: pcvl.BS.H() // x_rot(x) // pcvl.BS.H() 

start = y_rot(np.pi/4) // z_rot(-np.pi/4)  # Pour se placer sur le départ
delta = np.pi / 4
epsilon = np.pi / 4
zeta = np.pi / 4
eta =  np.pi / 4

# Une autre façon d'enchaîner les portes 
final_step = (start
                .add(0, z_rot(delta))
                .add(0, y_rot(epsilon))  # Arrivé à l'étape Hadamard
                .add(0, y_rot(zeta))
                .add(0, z_rot(eta))  # Fin du parcours !
             )

d = {
    "step_one": circuit_to_list(step_one),
    "step_two": circuit_to_list(step_two),
    "final_step": circuit_to_list(final_step)
}

URL = "https://perceval.challenges.404ctf.fr"
print(rq.get(URL + "/healthcheck").json())
print(rq.post(URL + "/challenges/1", json=d).json())