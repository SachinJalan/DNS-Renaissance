### Description of the Consumer ###
'''
The consumer will generate traffic of the form doamin_name, record_type. Every consumer will geneate traffic independently. Just like ICARUS.
The traffic generator will respect the trend we have seen empirically in the data we have collected.

The consumer can choose to locally cache the response it receives. It will have an appropriate replacement policy.

The consumer will collect metrics like resolution time, cache hit (Y/N) for each request it performs.
'''

import random
import numpy as np
from itertools import cycle
from datetime import datetime, timedelta
from subprocess import PIPE

from mininet.log import setLogLevel, info
from mininet.topo import Topo

from minindn.minindn import Minindn
from minindn.apps.app_manager import AppManager
from minindn.util import MiniNDNCLI, getPopen
from minindn.apps.nfd import Nfd
from minindn.apps.nlsr import Nlsr
from minindn.helpers.nfdc import Nfdc
from time import sleep
from collections import defaultdict


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

class TrafficGenerator:
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
        
        # Set seeds only if a seed is provided
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def _create_zipf_distribution(self, n, alpha):
        """
        Create a Zipf distribution for domain popularity.

        Parameters:
        - n: Number of domains.
        - alpha: Zipf distribution parameter.

        Returns:
        - A list of probabilities for each domain.
        """
        ranks = np.arange(1, n + 1)
        weights = 1 / np.power(ranks, alpha)
        return weights / weights.sum()

    def generate_traffic(self, n_requests):
        """
        Generate traffic events.

        Parameters:
        - n_requests: Number of traffic events to generate.

        Returns:
        - A list of traffic events in the format [<time-stamp>, <receiver>, <domain>, <rtype>].
        """
        traffic = []
        t_event = 0.0
        n_requests_copy = n_requests
        start_time = datetime.now()
        while(n_requests_copy > 0):
            # Generate inter-arrival time
            t_event += random.expovariate(self.rate)
            timestamp = start_time + timedelta(seconds=t_event)  # Convert t_event to a timestamp
            timestamp_str = timestamp.isoformat() + "Z"  # Format as ISO 8601 with 'Z' for UTC
            
            # Select a receiver randomly
            receiver = random.choice(self.receivers)

            # Select a domain based on Zipf distribution
            # domain_index = np.random.choice(len(self.domains), p=self.zipf_dist)
            domain_index = int(self.zipf.rv()) - 1
            domain = self.domains[domain_index]

            # Select a record type randomly for the chosen domain
            rtype = random.choice(self.domain_rtypes[domain])

            # Append the traffic event
            traffic.append([timestamp_str, receiver, domain, rtype])
            n_requests_copy -= 1
            if rtype == "A" and n_requests_copy > 0:
                t_event += random.expovariate(self.rate)
                timestamp = start_time + timedelta(seconds=t_event)  # Convert t_event to a timestamp
                timestamp_str = timestamp.isoformat() + "Z"  # Format as ISO 8601 with 'Z' for UTC
                traffic.append([timestamp_str, receiver, domain, "AAAA"]) 
                n_requests_copy -= 1

        return traffic
def classify_hosts(topology):
    """
    Classify hosts into receivers, ICR candidates, and source attachments based on their degree.

    Parameters:
    - topology: The topology object created from the .conf file.

    Returns:
    - A dictionary with keys 'receivers', 'icr_candidates', and 'source_attachments'.
    """
    # Calculate the degree of each node
    deg = defaultdict(int)
    for link in topology.links():
        node1, node2 = link
        deg[node1] += 1
        deg[node2] += 1

    # Classify nodes
    receivers = [v for v in topology.nodes() if deg[v] == 1]  # Nodes with degree 1
    icr_candidates = [v for v in topology.nodes() if deg[v] > 2]  # Nodes with degree > 2
    source_attachments = [v for v in topology.nodes() if deg[v] == 2]  # Nodes with degree 2

    return {
        "receivers": receivers,
        "icr_candidates": icr_candidates,
        "source_attachments": source_attachments,
    }


def run():
    Minindn.cleanUp()
    Minindn.verifyDependencies()
    geant_topo_path = "/home/mithilpn/projects/mini-ndn/topologies/geant.conf"
    topology, faces = Minindn.processTopo(geant_topo_path)

  # Classify hosts
    host_classification = classify_hosts(topology)
    receivers = host_classification["receivers"]
    icr_candidates = host_classification["icr_candidates"]
    source_attachments = host_classification["source_attachments"]

    # Add sources to the topology
    sources = []
    for v in source_attachments:
        u = f"source-{v}"  # Create a unique name for the source node
        topology.addHost(u)  # Add the source node to the topology
        topology.addLink(v, u, delay='10ms', bw=10)  # Add a link between the attachment node and the source
        sources.append(u)

    print("Receivers:", receivers, len(receivers))
    print("ICR Candidates:", icr_candidates, len(icr_candidates))
    print("Source Attachments:", source_attachments, len(source_attachments))
    print("Sources:", sources, len(sources))

    ndn = Minindn(topo=topology)
    ndn.start()

    info('Starting NFD on nodes\n')
    nfds = AppManager(ndn, ndn.net.hosts, Nfd)
    info('Starting NLSR on nodes\n')
    nlsrs = AppManager(ndn, ndn.net.hosts, Nlsr)
    sleep(10)

    print("Number of hosts: ", len(ndn.net.hosts)) 
    print("Number of switches: ", len(ndn.net.switches))
    print("Number of links: ", len(ndn.net.links))

    MiniNDNCLI(ndn.net)
    ndn.stop()

# Example usage
if __name__ == "__main__":
    # Example input
    domains = {
        "domain1": ["A", "AAAA", "CNAME"],
        "domain2": ["A", "AAAA", "CNAME"],
        "domain3": ["A", "AAAA", "CNAME"],
        "domain4": ["A", "AAAA", "CNAME"],
        "domain5": ["A", "AAAA", "CNAME"],
        "domain6": ["A", "AAAA", "CNAME"],
        "domain7": ["A", "AAAA", "CNAME"],
        "domain8": ["A", "AAAA", "CNAME"],
        "domain9": ["A", "AAAA", "CNAME"],
        "domain10": ["A", "AAAA", "CNAME"],
        "domain11": ["A", "AAAA", "CNAME"],
        "domain12": ["A", "AAAA", "CNAME"],
        "domain13": ["A", "AAAA", "CNAME"],
        "domain14": ["A", "AAAA", "CNAME"],
        "domain15": ["A", "AAAA", "CNAME"],
    }
    receivers = [f"reciever{i}" for i in range(1, 12)]  # Example receivers

    # Initialize the traffic generator
    generator = TrafficGenerator(domains, receivers, alpha=1.2, rate=5.0)

    # Generate traffic
    traffic = generator.generate_traffic(20)
    # Print the generated traffic
    for event in traffic:
        print(event)

    # n_replicas = 3
    # for _ in range(n_replicas):
    #     run()
    run()