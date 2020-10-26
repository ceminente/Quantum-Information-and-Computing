from quantum_state import evolution_from_protocol, spectral_time_evolution, compute_fidelity
import numpy as np
from random import choices
from random import uniform
from tqdm import tnrange
from copy import deepcopy


def exp_dec(iteration,percentage_flip,niterations):
    tau =  niterations/np.log(percentage_flip)
    return percentage_flip * np.exp(-iteration/tau)

def stochastic_descent(qstart, qtarget, L, T, dt, iterations, flips,exp_decay_flip, field_list,beta,metropolis_choice,verbose, check_norm):

    np.random.seed(213)

    nsteps = int(T/dt)

    random_protocol = np.array(choices(field_list, k=nsteps)) # Define a random protocol, sampling without replacement from a list. 
    temp_protocol=deepcopy(random_protocol)

    fidelity = compute_fidelity(qstart, qtarget)
    fidelity_values=[fidelity]
    flips_iter = flips
    for j in range(iterations):

        psi = deepcopy(qstart)
        if exp_decay_flip is True:
            flips_iter=int(exp_dec(iteration=j,percentage_flip=flips,niterations=iterations))

        index_update = np.random.randint(0, nsteps-1,size=int(nsteps/100*flips_iter)) # Select an index for the update.
        temp_protocol[index_update] = random_protocol[index_update]*(-1) # Try to update that index.
        
        evolution = evolution_from_protocol(psi, qtarget, temp_protocol, spectral_time_evolution, dt, L, make_gif=None)
        psi = evolution[-1]
        
        if check_norm and (np.abs(1 - compute_fidelity(psi,psi)) > 1e-13):
            print("Warning ---> Norm is not conserved")
            print(compute_fidelity(psi,psi))
            break

        temp_fidelity = compute_fidelity(qtarget, psi) # Evaluate the fidelity
        if temp_fidelity>fidelity: # Update the change only if better fidelity
            random_protocol=deepcopy(temp_protocol)
            fidelity=temp_fidelity
            #print("UPDATED ", "ITERATION N°",j )
            #best_reached_state = psi #unused but useful for debugging
        elif metropolis_choice is True:
            if np.random.uniform(0,1)<np.exp(-beta*(temp_fidelity-fidelity)):
                random_protocol=deepcopy(temp_protocol)
                fidelity=temp_fidelity
                #print("UPDATED LOWER FIDELITY ", "ITERATION N°",j )
                #best_reached_state = psi 
        fidelity_values.append(fidelity)

    return random_protocol, fidelity_values