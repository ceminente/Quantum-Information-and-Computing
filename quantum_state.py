'''
    Created on Oct 18, 2020

    @author: Alberto Chimenti

    Purpose: (PYTHON3 IMPLEMENTATION)
        Implementation of some qbit state manipulation functions
'''

### To read for further implementation:
# https://www.researchgate.net/publication/47744360_Spin_operator_matrix_elements_in_the_quantum_Ising_chain_Fermion_approach

#%%
import numpy as np
from scipy.constants import hbar
'''
    Global variable for easier use (BEWARE OF LOOP INDICES CHOICE)
'''
i = 0. + 1.j


###########################################_OLD_########################################
    
def hamiltonian(field, single=True):
    '''
        Flexible implementation of naive ising hamiltonian
    '''
    if single:
        H=np.array([[-1, -field],[-field, 1]], dtype=complex)
        return(H)
    else:
        pass

def time_evolution(psi, dt, field, euler=False):
    '''
    Function to implement time evolution for a pure quantum state.
    ! WARNING: as of 22.10.2020 exact method only implements time evolution 
               according to the hamiltonian H = -(Sx + field*Sz) for 1 QuBit.
    Inputs:
    # psi: np.array(dtype=complex), vector containing coefficients of the state to evolve
    # dt: float, timestep
    # field: float, magnetic field (parameter of the hamiltonian)
    #euler: boolean, if "True" time evolution operator is approximated using euler method. 
            If "False" exact method is used (spectral method).
            Default value is "False".
    Outputs:
    # psi: np.array(dtype=complex), vector containing coefficients of the evolved state.
    '''
    if euler:
        identity = np.diag(np.ones(len(psi)))
        psi = np.dot((identity -i*hamiltonian(field)*dt), psi)
        return(psi)
    else:
        hbar=1
        #------------------------CLARA---------------------------------------------------------------------
        if len(psi) == 2: #this method only works for one qubit
            #implements evolution using spectral method for one qubit
            #compute eigenstates of hamiltonian H = -(Sx + field*Sz) and normalize them
            ep_state = np.array([field - np.sqrt(1 + field*field), 1], dtype=complex)
            ep_state=ep_state/np.sqrt(np.vdot(ep_state,ep_state))
            em_state = np.array([field + np.sqrt(1 + field*field), 1], dtype=complex)
            em_state=em_state/np.sqrt(np.vdot(em_state,em_state))
            #compute eigenvalues
            ep_autoval = np.sqrt(1 + field*field)
            em_autoval = -np.sqrt(1 + field*field)
            #compute projections of the state to evolve over the eigenstates
            cp = np.vdot(ep_state,psi)
            cm = np.vdot(em_state,psi)
            #compute evolved state
            psi= cp * np.exp(- i * ep_autoval * dt / hbar) * ep_state + cm * np.exp(- i * em_autoval * dt / hbar) * em_state
            return psi
        else:
            pass
        #---------------------------------------------------------------------------------------------------
    
########################################################################################



def compute_fidelity(target, psi):
    F = np.abs(np.vdot(target, psi))**2
    return F


def generate_state(L):

    from functools import reduce
    from math import sqrt
    from random import gauss, uniform

    '''
    The function generates a random state for L qubits.

    Inputs:
    # L: integer, number of qubits

    Outputs:
    # np.array(dtype=complex), array of 2**L coefficients of the state
    '''

    coefficients = np.array([gauss(0.0, 1.0) for _ in range(2**(L+1))])
    norm = sqrt(reduce(lambda sum,x: sum + x*x, coefficients, 0.0))
    real = np.split(coefficients, 2)[0]
    imag = np.split(coefficients, 2)[1]
    return np.array([real / norm + 1.j*(imag / norm) for real,imag in zip(real,imag)],dtype=np.complex128)


def hamiltonian_LA(field, L=1, diag=True, g=1):

    '''
    This function writes the hamiltonian and (if "diag=True") compute its spectral quantities.
    The implemented hamiltonian depends on the number of qubits, L.
    If L==1: H = -field*Sx - g*Sz
    If L!=1: H = sum{n.n.}[ -Sz(i)Sz(i+1) - field*Sx(i) -g*Sz(i)]

    Inputs:
    #L: integer, number of qubits
    #field: float or integer, field along Sx
    #diag: boolean, if "True" also the spectral properties of H are computed
    #g: float or integer, field along Sz
    
    Outputs:
    #H: np.array(dtype=complex): hamiltonian
    #eigenval, eigenvect: specral properties of H (returned if diag="True")
    '''
    from numpy import linalg as LA

    #pauli matrices
    sigma_x=np.array([[0,1],[1,0]], dtype=complex)
    #sigma_y=np.array([[0,-1j],[1j,0]], dtype=complex) # INUTILE
    sigma_z=np.array([[1,0],[0,-1]], dtype=complex)
    sigma_z_interaction= np.kron(sigma_z,sigma_z)

    #create the hamiltonian according to the number of qubits
    if L == 1:
        H = -field*sigma_x - g*sigma_z

    else:
        H1 = np.zeros((2**L,2**L))
        H2 = np.zeros((2**L,2**L))
        H3 = np.zeros((2**L,2**L))

        for j in range(L-1):   
            H1 = np.kron(np.identity(2**j),sigma_z_interaction)
            H1 = np.kron(H1,np.identity(2**(L-j-2)))

        for j in range(L):
            H3 = np.kron(np.identity(2**j),sigma_x)
            H3 = np.kron(H3,np.identity(2**(L-j-1)))
            H2 = np.kron(np.identity(2**j),sigma_z)
            H2 = np.kron(H2,np.identity(2**(L-j-1)))

        H = -(H1 + g*H2 + field*H3)
        
    #if diag diagonalize and return spectral properties
    if diag:
        eigenval, eigenvect = LA.eig(H)
        return eigenval, eigenvect, H
    else:
        return H

def spectral_time_evolution(psi, dt, field, L=1):#, eigenvectors, eigenvalues):

    '''
    This function implements time evolution using the spectral method.
    Inputs:
    #psi: np.array(dtype=complex), coefficients of the state to evolve
    #field: float or integer, value of the magnetic field
    #L: integer, number of qubits
    #dt: float, timestep

    Outputs:
    #evolved_psi: np.array(dtype=complex), coefficients of the evolved state
    '''

    from scipy.constants import hbar
    hbar=1
    eigenvalues, eigenvectors, _ = hamiltonian_LA(field, L, diag=True)
    c_i = np.array([np.vdot(eigenvectors[:,i],psi) for i in range(len(psi))]) 
    temp_psi = []
    for i in range(len(psi)):
        temp_psi.append(c_i[i]*np.exp((-1j*eigenvalues[i]*dt)/hbar)*eigenvectors[i])
    evolved_psi = np.array(temp_psi).sum(axis=0)
    return evolved_psi


def evolution_from_protocol(qstart, qtarget, protocol, time_ev_function, dt, L, make_gif=None):
    import gif
    '''
    Provided a series of h field values this function evolve a qstart quantum state. If make_gid is not None
    it also plots the resulting evolution on the bloch sphere.

    Inputs:
    # qstart, qtarget: respectively the target ans start state
    # protocol: list, list of values of the field at each timestep
    # time_ev_func: function, function for time evolution
    # dt: float, timestep
    # L: int, number of qubits
    # create_gif = str, if None no gif is created, if present must be the name of the output gif

    Outputs:
    # qstates: list, list of states as np.arrays(dtype=complex)
    '''
    qstate = qstart

    qstates = [qstate]

    for h in protocol:
        qstate = time_ev_function(qstate, dt, h, L)
        qstates.append(qstate)
    
    if make_gif is not None:
        gif.create_gif(qstates, qstart, qtarget, make_gif)

    return qstates






###########################################################################################################
if __name__ == "__main__":

    H = hamiltonian_LA(-2)
    print(H[2])
    H = hamiltonian(-2)
    print(H)

    target = np.array([-1/np.sqrt(4) - 1/np.sqrt(4)*i, 1/np.sqrt(2) + 0.j])
    psi = np.array([+1/np.sqrt(4) + 1/np.sqrt(4)*i,1/np.sqrt(2) + 0.j])

    '''
    print(psi)
    for h in [-4, -2, 0, 2, 4]:
        print("Field=", h)
        print("\n")
        psi_trotter = time_evolution(psi, 0.05, h, euler=True)
        print("Trotter:", psi_trotter)
        print("Fidelity_trotter", compute_fidelity(psi_trotter, psi_trotter))
        print("\n")
        psi_spectral= time_evolution(psi, 0.05, h, euler=False)
        print("Spectral:", psi_spectral)
        print("Fidelity_spectral", compute_fidelity(psi_spectral, psi_spectral))
        print("\n")
        print("\n")
    #print(compute_fidelity(psi, psi))
    #print(1/np.sqrt(2))
    '''
    T_max = 1.8
    dt = 0.05#0.0000491
    h = [0]*int(T_max/dt)


    list_of_states = evolution_from_protocol(psi, target, h, spectral_time_evolution, dt, L= 1, make_gif="bloch_gif.gif")




#%%
