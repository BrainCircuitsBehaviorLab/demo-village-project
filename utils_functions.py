import numpy as np
import matplotlib.pyplot as plt


def sigmoid(x):
    return 1 / (1 + np.exp(-x))
def get_delay_probabilities(p, tau=0.08, gamma=3):
    """
    Compute a curriculum-based probability distribution over delay values.
    
    As learning progress increases, additional delays are introduced
    gradually and their probabilities grow smoothly. At p=0, only the
    easiest delays are likely; at p=1, all delays are equally likely.
    
    Parameters
    ----------
    p : float
        Learning progress in [0, 1].
    
    tau : float, optional
        Controls how smoothly new delays are introduced.
        Smaller values produce sharper transitions.
    
    gamma : float, optional
        Controls how slowly newly introduced delays gain probability.
        Larger values create a stronger curriculum effect.
    
    Returns
    -------
    delays : np.ndarray
        Available delay values (±10000 approximates ±∞).
    
    probabilities : np.ndarray
        Probability of each delay. Sums to 1.
    """
    delays = np.array([
        
         0, 0.1,
         0.25, 0.5,
         1, 10000
    ])

    thresholds = {
         1:     0.001,
         10000: 0.0,

         0.5:   0.25,

         0.25:  0.50,
         0.1:   0.65,
         0:     0.75,
    }

    weights = []

    for d in delays:
        t = thresholds.get(float(d), None)
        if t is None:
            raise ValueError(f"Missing threshold for delay {d}")

        if t == 0:
            # existing delays slowly lose dominance
            a = 1.0
        else:
            a = sigmoid((p - t) / tau)

        weights.append(a**gamma)

    weights = np.array(weights)

    probs = weights / weights.sum() #normalize so that it always sums 1

    return delays, probs

# ps = np.linspace(0, 1, 400)

# delays = np.array([
#      0,
#      0.25, 0.5,
#      1, 10000
# ])

# all_probs = []

# for p in ps:
#     _, probs = get_delay_probabilities(p)
#     all_probs.append(probs)

# all_probs = np.array(all_probs)

# plt.figure(figsize=(10, 6))

# for i, d in enumerate(delays):
#     label = "±∞" if abs(d) > 1000 else str(d)
#     plt.plot(ps, all_probs[:, i]*2, label=label)

# plt.xlabel("Learning progress p")
# plt.ylabel("Probability")
# plt.title("Delay probabilities as a function of learning progress")
# plt.legend()
# plt.grid(True, alpha=0.3)
# plt.show()
