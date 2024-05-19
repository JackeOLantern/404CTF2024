import numpy as np
import perceval as pcvl
import math
import random
from qiskit import *
from qiskit.visualization import plot_histogram
from qiskit.visualization import plot_bloch_multivector
from qiskit.quantum_info import Statevector


def circuit_to_state_vector(circuit):
    backend = pcvl.BackendFactory.get_backend("Naive")
    backend.set_circuit(circuit)
    backend.set_input_state(qubits["0"])
    ampl0, ampl1 = backend.prob_amplitude(qubits["0"]), backend.prob_amplitude(qubits["1"])
    return Statevector([ampl0, ampl1])
plot_bloch = lambda circuit: plot_bloch_multivector(circuit_to_state_vector(circuit))


# Une magnifique porte 
x_gate = pcvl.PERM([1, 0])


#x_gate2 = pcvl.PERM([2, 0, 1])
#pcvl.pdisplay(x_gate2)

# Une autre magnifique porte
hadamard_gate = pcvl.BS.H()
#pcvl.pdisplay(hadamard_gate)

qubits = {
    "0": pcvl.BasicState([1, 0]),
    "1": pcvl.BasicState([0, 1])
}
print("Le qbit 0 sur le premier rail :", qubits["0"])
print("Le qbit 1 sur le second rail :", qubits["1"])


# On crée une simulation de notre circuit : x_gate
p = pcvl.Processor("Naive", x_gate)

# On analyse la sortie produite avec un qubit 0 à l'entrée
#analyser = pcvl.algorithm.Analyzer(p, [qubits["0"]], '*')
#pcvl.pdisplay(analyser)

# Dictionnaire (inverse de qubit défini au dessus) servant à afficher directement les qubits lorsqu'on
# utilise des fonctions comme l'ananlyseur. 
qubits_ = {qubits[k]: k for k in qubits}

#print(" INIIAL ", qubits, " --> ", list(qubits.values()))
#print(" EN ENTREE ", qubits_)

#analyser = pcvl.algorithm.Analyzer(p, [qubits["0"]], '*')
#pcvl.pdisplay(analyser)





# Le '*' dans la définition précédente d'analyser servait à afficher toutes les sorties possible, ici,
# j'ai précisé quelles sorties je voulais pour les avoir dans l'ordre que je souhaite. 
'''analyser = pcvl.algorithm.Analyzer(
    p, 
    input_states=list(qubits.values()), 
    output_states=list(qubits.values()), 
    mapping=qubits_
)
pcvl.pdisplay(analyser)
pcvl.pdisplay(x_gate.definition())
pcvl.pdisplay(x_gate)
'''

'''
1]

p = pcvl.Processor("Naive", hadamard_gate)
analyser = pcvl.algorithm.Analyzer(
    p, 
    input_states=[qubits["0"]], 
    output_states=list(qubits.values()), 
    mapping=qubits_
)
pcvl.pdisplay(analyser)
#pcvl.pdisplay(hadamard_gate)

backend = pcvl.BackendFactory.get_backend("Naive")
backend.set_circuit(hadamard_gate)
backend.set_input_state(qubits["0"])
ampl0, ampl1 = backend.prob_amplitude(qubits["0"]), backend.prob_amplitude(qubits["1"])
print(f"|phi> = {ampl0} |0> + {ampl1} |1>")
'''
'''
phase_shifter = pcvl.PS(np.pi/3)
#pcvl.pdisplay(phase_shifter)

circuit_ps = pcvl.Circuit(2) // (0, phase_shifter)  # Le 0 correspond au numéro du rail où est positionné 
                                                    # notre composant 
pcvl.pdisplay(circuit_ps.compute_unitary())
#pcvl.pdisplay(circuit_ps)
backend_ps = pcvl.BackendFactory.get_backend("Naive")
backend_ps.set_circuit(circuit_ps)
backend_ps.set_input_state(qubits["0"])
ampl0, ampl1 = backend_ps.prob_amplitude(qubits["0"]), backend_ps.prob_amplitude(qubits["1"])
print(f"|phi> = {ampl0} |0> + {ampl1} |1>")
'''

'''
# STEP 1 Beam splitter
# On peut définir des variables symboliques : 
symbolic_alpha = pcvl.P('α')
simple_bs = pcvl.BS(theta=symbolic_alpha)
pcvl.pdisplay(simple_bs.U)
print("     ")
# Puis leur assigner une valeur : 
simple_bs.assign({'α': np.pi})
pcvl.pdisplay(simple_bs.compute_unitary())
step_one = simple_bs
#pcvl.pdisplay(step_one)

# pour 0.9
x = 2 * math.asin(math.sqrt(0.9))
simple_bs.assign({'α': x})

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
'''
'''
# STEP 2 Beam splitter
symbolic_beta = pcvl.P("β")
symbolic_gamma = pcvl.P("γ")
step_two_bs = pcvl.BS(theta=symbolic_beta)

step_two_ps = pcvl.PS(phi=symbolic_gamma)

step_two = step_two_bs // (1, step_two_ps)
#step_two = pcvl.BS(theta=symbolic_beta) // (1, pcvl.PS(phi=symbolic_gamma))
pcvl.pdisplay(step_two_bs.U)
print("x")
pcvl.pdisplay(step_two_ps.U)
print("=")
pcvl.pdisplay(step_two.U)

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
pcvl.pdisplay(step_two_bs.compute_unitary())
pcvl.pdisplay(step_two_bs)
'''
super_preparator = pcvl.BS()

phi_tl, phi_tr, phi_bl, phi_br, theta_ = [round(random.uniform(0, np.pi), 2) for _ in range(5)]
super_preparator = pcvl.BS(phi_tl=phi_tl, phi_tr=phi_tr, phi_bl=phi_bl, phi_br=phi_br, theta=theta_)
pcvl.pdisplay(super_preparator.U)

#pcvl.pdisplay(super_preparator)
backend = pcvl.BackendFactory.get_backend("Naive")
backend.set_circuit(super_preparator)
backend.set_input_state(qubits["0"])

ampl0, ampl1 = backend.prob_amplitude(qubits["0"]), backend.prob_amplitude(qubits["1"])

print(f"|φ> = {np.round(ampl0, 2)} |0> + {np.round(ampl1, 2)} |1>")
#state_vector = Statevector([ampl0, ampl1])  # À ne pas confondre avec StateVector de Perceval
#plot_bloch_multivector(state_vector)
#plot_bloch_multivector(np.array(qubits["0"]))  # Même chose que plot_bloch_multivector([1, 0])
#plot_bloch_multivector(np.array(qubits["0"]))  # Même chose que plot_bloch_multivector([1, 0])
#plot_bloch(hadamard_gate)
#pcvl.pdisplay(super_preparator)

x_rot = lambda x: pcvl.Circuit(2) // (0, pcvl.PS(np.pi)) // pcvl.BS.Rx(theta=x) // (0, pcvl.PS(np.pi)) 
y_rot = lambda x: pcvl.BS.Ry(theta=x)
z_rot = lambda x: pcvl.BS.H() // x_rot(x) // pcvl.BS.H() 

#the_way = x_rot(-np.pi/4) // z_rot(-np.pi/4)
#plot_bloch(the_way)
'''

start_state = np.array([np.sqrt(2+np.sqrt(2))/2, np.sqrt(2-np.sqrt(2))/2 * (np.sqrt(2)/2 - 1j * np.sqrt(2)/2)])
plot_bloch_multivector(start_state)
step_state = np.array([np.sqrt(2)/2, -np.sqrt(2)/2])
plot_bloch_multivector(step_state)


'''

finish_state = np.array([np.sqrt(2-np.sqrt(2))/2, np.sqrt(2+np.sqrt(2))/2 * (np.sqrt(2)/2 + 1j * np.sqrt(2)/2)])
plot_bloch_multivector(finish_state)

start = y_rot(np.pi/4) // z_rot(-np.pi/4)  # Pour se placer sur le départ

delta = np.pi / 4
epsilon = np.pi / 4

## way = y_rot(np.pi/4) // z_rot(-np.pi/4) // z_rot(delta) // y_rot(epsilon) # H
## plot_bloch(way)
zeta = np.pi / 4
eta =  np.pi / 4

way = y_rot(np.pi/4) // z_rot(-np.pi/4) // z_rot(delta) // y_rot(epsilon) // y_rot(zeta) // z_rot(eta) 

plot_bloch(way)

# Une autre façon d'enchaîner les portes 
final_step = (start
                .add(0, z_rot(delta))
                .add(0, y_rot(epsilon))  # Arrivé à l'étape Hadamard
                .add(0, y_rot(zeta))
                .add(0, z_rot(eta))  # Fin du parcours !
             )
plot_bloch(final_step)

pcvl.pdisplay(super_preparator)