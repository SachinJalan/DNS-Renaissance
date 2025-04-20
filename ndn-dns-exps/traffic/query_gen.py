import random
import numpy as np
from datetime import datetime, timedelta

class DiscreteDist:
    """Implements a discrete distribution with finite population.

    The support must be a finite discrete set of contiguous integers
    {1, ..., N}. This definition of discrete distribution.
    """

    def __init__(self, pdf, seed=None):
        """
        Constructor

        Parameters
        ----------
        pdf : array-like
            The probability density function
        seed : any hashable type (optional)
            The seed to be used for random number generation
        """
        if np.abs(sum(pdf) - 1.0) > 0.001:
            raise ValueError("The sum of pdf values must be equal to 1")
        random.seed(seed)
        self._pdf = np.asarray(pdf)
        self._cdf = np.cumsum(self._pdf)
        # set last element of the CDF to 1.0 to avoid rounding errors
        self._cdf[-1] = 1.0

    def __len__(self):
        """Return the cardinality of the support

        Returns
        -------
        len : int
            The cardinality of the support
        """
        return len(self._pdf)

    def pdf(self):
        """
        Return the Probability Density Function (PDF)

        Returns
        -------
        pdf : Numpy array
            Array representing the probability density function of the
            distribution
        """
        return self._pdf

    def cdf(self):
        """
        Return the Cumulative Density Function (CDF)

        Returns
        -------
        cdf : Numpy array
            Array representing cdf
        """
        return self._cdf

    def rv(self):
        """Get rand value from the distribution"""
        rv = random.random()
        # This operation performs binary search over the CDF to return the
        # random value. Worst case time complexity is O(log2(n))
        return int(np.searchsorted(self._cdf, rv) + 1)

class TruncatedZipfDist(DiscreteDist):
    """Implements a truncated Zipf distribution, i.e. a Zipf distribution with
    a finite population, which can hence take values of alpha > 0.
    """

    def __init__(self, alpha=1.0, n=1000, seed=None):
        """Constructor

        Parameters
        ----------
        alpha : float
            The value of the alpha parameter (it must be positive)
        n : int
            The size of population
        seed : any hashable type, optional
            The seed to be used for random number generation
        """
        # Validate parameters
        if alpha <= 0:
            raise ValueError("alpha must be positive")
        if n < 0:
            raise ValueError("n must be positive")
        # This is the PDF i. e. the array that  contains the probability that
        # content i + 1 is picked
        pdf = np.arange(1.0, n + 1.0) ** -alpha
        pdf /= np.sum(pdf)
        self._alpha = alpha
        super().__init__(pdf, seed)

    def alpha(self):
        return self._alpha

class DnsTrafficGenerator:
    def __init__(self, domains, receivers, alpha=1.0, rate=1.0, seed=None):
        """
        Initialize the traffic generator.

        Parameters:
        - domains: Dictionary of domains with record types {domain: [rtype1, rtype2, ...]}.
        - receivers: List of receivers.
        - alpha: Zipf distribution parameter for domain popularity.
        - rate: Average request rate (requests per second).
        - seed: Random seed for reproducibility. If None, random behavior is non-deterministic.
        """
        self.domains = list(domains.keys())
        self.domain_rtypes = domains
        self.receivers = receivers
        self.alpha = alpha
        self.rate = rate
        self.zipf = TruncatedZipfDist(alpha, len(self.domains))

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def generate_traffic(self, n_requests, n_warmup_requests=0):
        """
        Generate traffic events.

        Parameters:
        - n_requests: Number of traffic events to generate.

        Returns:
        - A list of traffic events in the format [<time-stamp>, <receiver>, <domain>, <rtype>].
        """
        traffic = []
        t_event = 0.0
        start_time = datetime.utcnow()

        n_requests_copy = n_requests + n_warmup_requests
       
        while(n_requests_copy > 0):
            log = n_requests_copy <= n_requests
            t_event += random.expovariate(self.rate)
            timestamp = start_time + timedelta(seconds=t_event)  
            timestamp_str = timestamp.isoformat() + "Z"  
            receiver = random.choice(self.receivers)
            domain_index = int(self.zipf.rv()) - 1
            domain = self.domains[domain_index]
            rtype = random.choice(self.domain_rtypes[domain])
            traffic.append({"timestamp":timestamp_str, "reciever":receiver, "domain":domain, "rtype":rtype, "log":log}) 
            n_requests_copy -= 1
            if rtype == "A" and n_requests_copy > 0:
                log = n_requests_copy <= n_requests
                t_event += random.expovariate(self.rate)
                timestamp = start_time + timedelta(seconds=t_event)  # Convert t_event to a timestamp
                timestamp_str = timestamp.isoformat() + "Z"  # Format as ISO 8601 with 'Z' for UTC
                traffic.append({"timestamp":timestamp_str, "reciever":receiver, "domain":domain, "rtype":"AAAA", "log":log}) 
                n_requests_copy -= 1

        return traffic