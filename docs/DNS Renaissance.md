## Mom 5-11 3:00pm

Every domain has name. You query that name (rewrite)

Ndn info does not need to be in one packet

Icarus  
Routers  
Some producers some consumers

## genda

- 1st rank in poster presentation  
- submit paper if possible  
- mae topology

## Protocol-Level Inefficiencies in Current DNS Implementation

Visualisations

1. All plots in first report  
2. Visualisation to show that   
   **Authoritative Answer (AA)**: Always set to 0, indicating non-authoritative responses.  
   **Reserved Bit (Z)**: Always set to 0\.  
   **Question Count (QDCOUNT)**: Always set to 1, limiting each packet to one question.  
   **Name Server Count (NSCOUNT)**: Always set to 0, indicating no additional authoritative information.  
   **Additional Records Count (ARCOUNT)**: Always set to 0, limiting extra information sharing.  
   Basically almost 7 bytes are always seen to be not used.  
3. Plots to show that a very little percentage of the queries have answers that are so large DNS had to switch to TCP. all except one in all these cases were queries for AAAA records.

## Evaluating DNS Path Efficiency: Recursive vs. Iterative vs. Delegated Modes

Visualisations

1. Plots in `plot-delegation.ipynb`  
2. Visual representation to show that very little percentage benefit from delegation.   
3. A visualization to show why only a few benefit from delegation (lack for  straight path).  
   

## Exploring Router-Level DNS Caching for Improved Resolution Times

Visualisations

1. Diagram showing how caching in a router common to two sub nets can help reduce DNS resolution time.  
2. Worstcase to bestcase time comparison.

## Critical Notes

What is it we want? 

- 

Where are we at?

- context setup

There is definitely that needs to be done wrt dns  
Edge, mobile, iot, power

We have to ramp up from 3 differents prospects 

- DNS Protocol level  
  - Currently only one question allowed  
  - Experiment shows multiple dns queries for visiting single page  
  - Qtype, Qclass, etc  
- Efficient way to DNS path  
  - Recursive  
  - Iterative   
  - Asked in computer networks  
  - People worked on it but got rejected due to security reasons  
  - Delegation model (if security is there and dns protocol level revamp)  
  - Use dig with appropriate flags  
    - Get rtt and you get the authoritative values  
    - Ping authoritative server directly   
    - Analyzes difference in latency  
- Name data networking (NDN) / ICN  
  - Caching  
  - If iitgn asks for google.com and gift city is also asks for same domain then no need to go all the way  
  - Traceroute and you will get router hops  
  - Similar to previous prospect and analyze difference in latency  
  - Best case is we find cache in first hop  
  - Overlay network (doesn’t work on IP)

There handful (7-13) main dns provider but using CDN we get thousands of server spreading across whole world

Discussion on

- Overhead  
- Is query broken in multiple packet  
- Is answer broken in multiple packet  
- Are there any dns spanned over multiple packets or switched to tcp  
- In guideline if answer is large then switch over to tcp

## MoM: Pre meeting

Problems

- DNS is the backbone.  
- Unutilized potential  
- Question section repeated in answer packet  
- Only one domain per question  
- Multiple answers but top answer is always chosen  
- TTL values too short  
- Recursive resolving related issues (latency pain point) .  
- Centralization risk  
- Domain being queried is visible to everyone  
- Physical location is also revealed (IDK)   
- DNSSEC is complex

Other work

- DoT  
- DoH  
- DoQ

Beneficiary

- Edge devices

Our DNS

- multiple queries in single request-response  
- has to be compatible with current dns  
- low power  
- effective   
- backhaul

Experiments and Analysis

## current dns

Here's a detailed table of the DNS structure, including the length of each section in bits:

**DNS Header**

| Section | Length (bits) | Description |
| :---: | :---: | :---: |
| ID | 16 | Unique identifier for the DNS message |
| QR | 1 | Query/Response flag (0 \= query, 1 \= response) |
| OPCODE | 4 | Operation code (e.g., 0 \= query, 2 \= status) |
| AA | 1 | Authoritative answer flag (0 \= non-authoritative, 1 \= authoritative) |
| TC | 1 | Truncation flag (0 \= not truncated, 1 \= truncated) |
| RD | 1 | Recursion desired flag (0 \= not desired, 1 \= desired) |
| RA | 1 | Recursion available flag (0 \= not available, 1 \= available) |
| Z | 3 | Reserved for future use |
| RCODE | 4 | Response code (e.g., 0 \= no error, 3 \= name error) |
| QDCOUNT | 16 | The number of entries in the Question Section |
| ANCOUNT | 16 | The number of entries in the Answer Section |
| NSCOUNT | 16 | The number of entries in the Authority Section |
| ARCOUNT | 16 | The number of entries in the Additional Section |
| **total** | **32 \+ 16\*4 \= 96** |  |

**DNS Question**

| Section | Length (bits) | Description |
| :---: | :---: | :---: |
| QNAME | variable (multiple of 8\) | Domain name being queried |
| QTYPE | 16 | Type of query (e.g., 1 \= A, 2 \= NS, 5 \= CNAME) |
| QCLASS | 16 | Class of query (e.g., 1 \= IN, 2 \= CS, 3 \= CH) |
| **total** | **8q \+ 32** |  |

**DNS Answer**

| Section | Length (bits) | Description |
| :---: | :---: | :---: |
| NAME | variable (multiple of 8\) | Domain name being answered |
| TYPE | 16 | Type of answer (e.g., 1 \= A, 2 \= NS, 5 \= CNAME) |
| CLASS | 16 | Class of answer (e.g., 1 \= IN, 2 \= CS, 3 \= CH) |
| TTL | 32 | Time to live (in seconds) |
| RDLENGTH | 16 | Length of the RDATA section (in bytes) |
| RDATA | variable (multiple of 8\) | Answer data (e.g., IP address, name server) |
| **total** | **8a \+ 8b \+ 80** |  |

**total: 32 \+ 16\*4 \+ 8q \+ 32 \+ 8a \+ 8b \+ 80 \= 8(q+a+b) \+ 240**

**Authority Section**:  
Provides details about the authoritative name servers responsible for the domain, often containing NS records.

**Additional Section**:  
Provides additional information, such as IP addresses for the nameservers (A or AAAA records for the nameservers themselves).  
![][image1]  
we can clearly see under utilization (and no utilization of bits) for some cases  
we can optimize this 

## Literature Survey (Research Works)

1) [https://ieeexplore.ieee.org/document/8651739](https://ieeexplore.ieee.org/document/8651739)  
2) [https://www.semanticscholar.org/paper/CoDNS%3A-Improving-DNS-Performance-and-Reliability-Park-Pai/ad2b0ca8df37ef4580ba64bf37e6635ae80e1bab](https://www.semanticscholar.org/paper/CoDNS%3A-Improving-DNS-Performance-and-Reliability-Park-Pai/ad2b0ca8df37ef4580ba64bf37e6635ae80e1bab)  
3) [https://github.com/kaustubhshan27/doh-do53-overhead-analysis/blob/main/paper/doh-do53-analysis.pdf](https://github.com/kaustubhshan27/doh-do53-overhead-analysis/blob/main/paper/doh-do53-analysis.pdf)

## todo

- [x] ~~abstract~~  
- [x] ~~introduction | problem definition~~  
- [x] ~~experiments~~  
      - [x] ~~methodology~~  
      - [x] ~~results and plots~~  
      - [x] ~~inference~~  
- [x] ~~current DNS and what can be improved~~  
- [x] ~~challenges~~  
- [x] ~~conclusion~~  
- [ ] perform experiment for mobile (use browser agent i suppose)  
- [ ] add more references and citations (use ai ig)  
- [ ] list problems in current dns stack  
- [ ] add plot which show timeline of dns stuff per domain  
- [ ] dnssec??  
- [ ] 

## report

### Abstract

current dns not good. need better one from scratch. first study existing. find weakness. make new strong one. compare to existing.

The Domain Name System (DNS) protocol has remained unchanged since its inception in 1983\. While it is efficient for general computing, the increasing importance and number of edge devices and IoT may reveal that the current DNS protocol implementation can be power-hungry, slow and insecure. We claim that the DNS protocol implementation has inefficiencies that cause overheads in resource-constrained environments, such as IoT devices with limited energy budgets. The project we undertake this semester investigates the inefficiencies of the current DNS protocol implementation and identifies opportunities for optimization. The results show some aspects the implementation could improve through sandboxed packet capture and analysis of DNS traffic from the top 1000 websites.

### introduction

dns \- domain name resolution  
What is DNS? Implementation details? Common patterns about records

The Domain Name System (DNS) is a naming system that translates human-readable domain names, like "iitgn.ac.in," into IP addresses like 72.1.241.188, that machines use to address each other. Usually, all of the DNS operates using a recursive query mechanism, where a DNS resolver iteratively queries multiple DNS servers to resolve a domain name, starting from the root servers (contain info about .com, in, etc...) through the top-level domain (TLD) servers (provide .com, .in,  etc...), and down to the authoritative servers. While the protocol supports issuing multiple queries simultaneously, current implementations typically handle one query at a time, leading to inefficiencies, especially when resolving domains where more than one query is necessary. For example, for iitgn.ac.in alone, we have 38 queries to multiple domains like px.ads.linkedin.com, www.facebook.com, www.googletagmanager.com, cdnjs.cloudflare.com. Also, we can see some common patterns. For instance, when a DNS query requests an NS (Name Server) record for a domain, it is common for  A or AAAA record queries after NS record query. We can do this together, too, and optimise the process.

### experiment

gathering performance results for current dns using **this methodology**   
tell about our scripts and stuff  
parameters  
results and plots  
Inferences

### what scope

inefficient query / response  
unnecessary bit fields  
overheads of dnssec  
clearly visible in results and plots

### challenges

was very tough to collect data

### conclusion

we can make something beautiful

# Tasks

- [ ] Get Time for the first byte.  
- [ ] Get number of and Ratio of DNS packets.  
- [ ] Get Time taken in DNS resolution.  
- [ ] Get power consumption and CPU  cycles on PC and Mobile devices.  
- [ ] 

TOOLS:

1) Dnspeep  
2) Mitmproxy  
3) Dns\_parser crate in Rust

# LITERATURE REVIEW

PARAMETERS \\

1) DNS component of Page load time  
2) DNS component of Bandwidth  
3) DNS query response time

problems  
attack on dns \> whole infrastructure down  
location of access  
vulnerable to several attacks  
bcz uses just udp

other work  
dns over tls  
dns over https  
dns over quic

security and privacy parts

privacy not always good especially if concerns in increase computation 

IoT usecase focused dns required 

sequential and staggered dns requests adds unnecessary cost 

our dns  
multiple queries in single request-response  
has to be compatible with current dns  
low power  
effective   
backhaul

tasks  
empirically showcase the current problems  
examine dns stuff while we visit google.com in browser

projects  
dnssec  
dein???  
whereas using UDP makes DNS usable for distributed  
denial-of-service attacks \[2\]. \-\> Nani DDoS → More Nani)

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Work:

1) Monitoring performance  
2) 

## links

[https://github.com/EmilHernvall/dnsguide/blob/b52da3b32b27c81e5c6729ac14fe01fef8b1b593/chapter1.md](https://github.com/EmilHernvall/dnsguide/blob/b52da3b32b27c81e5c6729ac14fe01fef8b1b593/chapter1.md)

Github: [https://github.com/kaustubhshan27/doh-do53-overhead-analysis/tree/main](https://github.com/kaustubhshan27/doh-do53-overhead-analysis/tree/main)  
[https://github.com/noise-lab/dns-measurement](https://github.com/noise-lab/dns-measurement)  
[https://github.com/mgranderath/dnsperf](https://github.com/mgranderath/dnsperf)   
[https://github.com/mgranderath/misc-dns-measurements](https://github.com/mgranderath/misc-dns-measurements)   
[https://github.com/SIDN/pqc-dnssec-measurement](https://github.com/SIDN/pqc-dnssec-measurement)   
[https://github.com/zmap/zdns](https://github.com/zmap/zdns)

[https://ui.perfetto.dev/](https://ui.perfetto.dev/)  
chrome://net-export/      [https://netlog-viewer.appspot.com/\#import](https://netlog-viewer.appspot.com/#import)

Overview of dns and risks \-\> [https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=\&arnumber=9520679](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9520679)   
[https://www.sciencedirect.com/science/article/pii/S1574013722000132](https://www.sciencedirect.com/science/article/pii/S1574013722000132) 

# meetings

## 23 sept

Number of dns resolutions that happen when a visitor visit a website – histogram of dns queries, histogram of record types  
Just the count – histogram of byte ratio, histogram of packet ratio,   
Example 10 percent of website require 3 dns resolution  
Like cdf how many dns resolutions were happening   
Second most crititcal latency  
Time to first byte, how much dns resolution time   
How many sites, pdf with bin size 

Total bytes contributed by the dns , vs the bytes actually downloaded.  
Percentage of data download

Number of compute cycles in dns resolution. Associated power used in dns resolution.

Put number of domains visited on the y axis  
How much time spent in domain resolution vs ttfb  
And time in dns vs entire page ☆  
Dns bytes vs total bytes for the page if above 5 to 10 percent is critical

Each record type is different make that differentiation for the plots

If i have nx record serperate aa record seperate multiple packets thus we need to do something, can i built a system which can bring up the response  
If 10 percent is more, no user

pdf, cdf of ratio plots  
add inferences in report  
examine potential improvements in current dns  
number of dns resolution   
see if something can be done on android  
browser agent of android 

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAt0AAAFjCAYAAADhH7dqAABLqElEQVR4Xu3dC7RvVVXHcV5eQF4XfF9UEMnwlVLmQPKRSNBQhuJINLXBJStNISOGqA0tSBJtOIwUwUb5IF+DcthVC9JMwVSENEEQn5AaopIv1ASugDv39s5/8/yYa+21z3//93+dw/czxhrrP+eaa519/+x79vR47jnbNQAAAAAWajtNAAAAABgXTTcAAACwYDTdAAAAwILRdAMAAAALRtMNAAAALBhNNwAAALBgNN0AAADAgtF0AwAAAAtG0w0AAAAsGE03AAAAsGA03QAAAMCC0XQDAAAAC0bTDQAAACwYTTcAAACwYDTdAAAAwILRdAMAAAALRtMNAAAALBhNNwAAALBgNN0AAADAgtF0AwAAAAtG0w0AAAAsGE03AAAAsGA03QAAAMCC0XQDAAAAC0bTDQAAACwYTTcAAACwYDTdAAAAwILRdAMAAAALRtMNAAAALBhNN4AqvfnNb2622267bvzqr/7qLN/GrY997GPN9773vVm+RHvml7/8ZU0XsY9rnvCEJ4R574wzztBUFdprfstb3rIi95jHPKbL77HHHs1v/dZvrVjzf8YLLrigeec739m9vvzyy5t73/vezaZNm5rXvva1sxpj//1+4Rd+obnpppt0OSn3nnqp97fdv/322zcPetCDmosvvliXV3j5y1+uKQBYiLLPbAAwsbZB/sQnPtG9/u53v9s84xnPWLH+qle9atUN9GpoI2hNd85+++2nqSo88IEP1FTXdJtbbrllxZ+3rf+DP/iD7rVvuu9yl7vMaq677rrZa7Pbbrt186233nqb9y+ntDb1/vr/NkcffXRz9tlnu9WV7BoBYNHKPrMBwMR80/2Tn/ykOfbYY7vX1pDZV1G1QTv44INnr23t3HPPbT772c+u+Er3EUcc0eyyyy7Nb//2b3dx2xg+4AEPaO5617t2Tb7Sj6Nf6f7BD37QNYFtI/qf//mfs68c23rblLZnt1/1Nd/+9re7ryy3fzar27x5c3PVVVc1u+++exc/5SlPaTZs2NCceOKJs31to9h+/PYrzK3HPvax3VecIyeddFK3v/0fKa3U++ab7lb7Xlx//fXd6/Zjte9Vyzfd/v+BiPiGtv143/nOd7qvPrd/5ssuu2y2dsoppzQ777xz8+QnP3lW22r/u9/hDnfoXr/1rW/truFpT3taF+v76/mm+4c//GGz7777dq/b92CfffZpfvEXf3G2bme07/tXvvKV5n73u19XM+X/oANw+3Dbz1YAUAH/7SVtQ2asyUp9pbttCNsG+73vfW/zxCc+sctZo2tN95YtW2YNvfHNW9TI+Wa1Hdp077XXXr68478Sa3U//vGPZw215fxXgtvm78UvfvHPNjmveMUrmq9+9avda6ttv72m/TaK1uc///muefXe/e53N3/+53/evW6b97aZb/V9pbvVvkevec1rutftn7X9Hydf//rXVzTdO+64Y/OIRzyief/73++3zrRN97e+9a3m9NNPv823mNh/0ze96U3NX/7lX87yrfbPd/PNNze77rprF7fNsH0byBVXXDF7XfKV7pa9XzfccEM3t/8NDjvssO61/x8Gtt6K7gEAmAefVQBUyX+lu21K73GPe3Svo6a7/QrqN77xjdlXZp/5zGc2hxxySPPpT3+6ufrqq2d7rOluv4La5tqm3BpBbaqV5rTp/vu///tmhx12WNH4+qbwUY961Oy17fFfnfZNd/vnNW1s1/R3f/d3Xc6+6tw66KCDZq+POuqo2evWkUceOXvdvjcveMELuterabpb7cf1TXdr69atzR//8R/PviLttfUf+MAHmmuuuaaL2z/XgQceuOI99tdv9L/Bc5/73BX/bex/RA1tuv/pn/6pa/bb2P7Hijbd97znPW/z8QFgDHxWAVAl33S3rAmy2Tfd9q0GbYPaapvZtglsm7xzzjln9pVl/+0lH//4x5tf+qVfmjWg7bd+tA2iDaVNmDbdrbPOOqu54x3v2Jx//vldvNqm27TfW33nO9+5+4p1++dor7/lG0XfQGuzOU/TfdpppzXnnXde99rO3WmnnW7TdBt9f1r6/dLtmc961rO6r4zbNaSa7nbvjTfe2MXPec5zmve9732z/zbtf7vW0Ka7bbTf+MY3dmdYzl/j7/zO73TfjvOv//qvzZ3udKdZHgDGcNvPkgBQAd90t98O0H5fcsuapde//vXNpZdeOqv32pqHPvSh3ev999+/a/Za1nT779nWZr7VfmuD0qZSm277KnvrYQ97WDdv3LhxlrO69uy+by8x7U8HaZvtVvvxhjbdbbPefmtHq/1e6NJvL9F/SGnntvvb99Wa7vb/MTD6/rS06dbvpW6lvr2k1Tb5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5fS0uYtmo3EtUo1qbrbXQ/bk5tRZnl/3OZ2js3QfAGDtoL8pw6NuQtyU09MmT5s9ra2NXrdee2q217pH49I5tdeL1qM5OisXp/j1vloAwOLQ35ThUbXNd7/73eahD31oc/DBB8/G2Lgpp6dNnjZ3WlsbvW699tRsr3WPxqVzaq8XrUdzdFYuTvHrfbUAgMWhvynDo2pC3JTT0yZPmzutrY1et157arbXukfj0jm114vWozk6Kxen+PW+WgDA4tDflOFRtc3ee+99m5GyYcOG5sorr2w2btyoS82+++7bPOlJT9J0h5tyetrkaXOntbXR69ZrT832WvdoXDqn9nrRejRHZ+XiFL/eVwsAWBz6mzI8qrY555xzbjNSjj/++G7etGnTivwtt9zSvOENb6Dprog2edrcaW1t9Lr12lOzvdY9GpfOqb1etB7N0Vm5OMWv99UCABaH/qYMjyrHbprczXPttdc2F110Uff65JNPXrHWfpW7pU33Kaec8tOmYLtupM7FYmiTp82d1tZGr1uvPTXba92jcemc2utF69EcnZWLU/x6Xy0AYHFyfRP+H4+qbdpfhtP+9kk/Ilu3bm22bNnSvT722GNn+UsvvbTZcccdu9H+6MGrrrpqtma4KaenTZ42d1pbG71uvfbUbK91j8alc2qvF61Hc3RWLk7x6321AIDFob8pw6NqFU444YRutq9st2688cbmiiuu6Eb76+Tb5lxxU05Pmzxt7rS2Nnrdeu2p2V7rHo1L59ReL1qP5uisXJyi9QCA5aC/KcOjyml/Dfy97nWv5slPfnKz55576vLMmWee2f1jyosvvriLN2/evGJdv73EcFNOT5s8be60tjZ63Xrtqdle6x6NS+fUXi9aj+borFycovUAgOWgvynDo8rZZZddZq8///nPu5VxcFNOT5s8be60tjZ63Xrtqdle6x6NS+fUXi9aj+borFycovUAgOWgvynDo8o59NBDZ6/t+7bHxE05PW3ytLnT2trodeu1p2Z7rXs0Lp1Te71oPZqjs3JxitYDAJaD/qYMj6ptdthhh+4fQPoxNm7K6WmTp82d1tZGr1uvPTXba92jcemc2utF69EcnZWLU7QeALAc9DdleFRNiJtyetrkaXOntbXR69ZrT832WvdoXDqn9nrRejRHZ+XiFK0HACwH/U0ZHlWi/U2T73nPe7oxNm7K6WmTp82d1tZGr1uvPTXba92jcemc2utF69EcnZWLU7QeALAc9DdleFQ5Rx11VPOtb32r+exnP9s8/OEP1+W5cVNOT5s8be60tjZ63Xrtqdle6x6NS+eSvX3rWhflNLZcROtT+tYBAPOhvynDo8jZuHFjN3/oQx8Kf7nNvLgpp6cNnDZ3WlsbvW699tRsr3WPxqVzyd6+da2LchpbLqL1KX3rAID50N+U4VHkvO997+vmn//5n2/ufOc7y+r8uCmnpw2cNndaWxu9br321GyvdY/GpXPJ3r51rYtyGlsuovUpfesAgPnQ35ThUZTwk5/8RFNz46acnjZw2txpbW30uvXaU7O91j0al84le/vWtS7KaWy5iNan9K0DAOZDf1OGR5Fz8803d7+Jsv3xgS95yUt0eW7clNPTBk6bO62tjV63Xntqtte6R+PSuWRv37rWRTmNLRfR+pS+dQDAfOhvyvAocvyvfj/vvPPcyji4KaenDZw2d1pbG71uvfbUbK91j8alc8nevnWti3IaWy6i9Sl96wCA+dDflOFR5NzlLneZvW5/gsnYuCmnpw2cNndaWxu9br321GyvdY/GpXPJ3r51rYtyGlsuovUpfesAgPnQ35ThUbTNk5/85G60/4DycY973Iqveo+Fm3J62sBpc6e1tdHr1mtPzfZa92hcOpfs7VvXuiinseUiWp/Stw4AmA/9TRkeRRPippyeNnDa3GltbfS69dpTs73WPRqXziV7+9a1LsppbLmI1qf0rQMA5kN/U4ZHkfif//mf5iMf+YimR8FNOT1t4LS509ra6HXrtadme617NC6dS/b2rWtdlNPYchGtT+lbBwDMh/6mDI8i59nPfnZz/vnndzfOfe97X12eGzfl9LSB0+ZOa2uj163Xnprtte7RuHQu2du3rnVRTmPLRbQ+pW8dADAf+psyPIqcXXfddfb6M5/5jFsZBzfl9LSB0+ZOa2uj163Xnprtte7RuHQu2du3rnVRTmPLRbQ+pW8dADAf+psyPIqcww47rLnxxhu718ccc4yszo+bcnrawGlzp7W10evWa0/N9lr3aFw6l+ztW9e6KKex5SJan9K3DgCYD/1NGR5F4m/+5m+ak046qbnhhht0aW7clNPTBk6bO62tjV63Xntqtte6R+PSuWRv37rWRTmNLRfR+pS+dQDAfOhvyvAocjZt2qSpUXFTTk8bOG3utLY2et3+2jXWOarRuHSO9qZizesc1aRiy0W0PiVa13hMizwbAGpEf1OGx4Nz9NFHN/e4xz1mP7N7bNyU09MGzjdg2hxpXAO9bn/tGusc1WhcOkd7U7HmdY5qUrHlIlqfEq1rPKZFng0ANaK/KcPjwTnuuONWjLFxU05PGzjfgGlzpHEN9Lr9tWusc1Sjcekc7U3Fmtc5qknFlotofUq0rvGYFnk2ANSI/qYMj4dtbr311ubQQw9tXvSiF+nSaLgpp6cNnG/AtDnSuAZ63f7aNdY5qtG4dI72pmLN6xzVpGLLRbQ+JVrXeEyLPBsAakR/U4bHwzYHHnhgN3/gAx/oGvBF4KacnjZwvgHT5kjjGuh1+2vXWOeoRuPSOdqbijWvc1STii0X0fqUaF3jMS3ybACoEf1NGR4P22zYsGH2+pprrnEr4+GmnJ42cL4B0+ZI4xrodftr11jnqEbj0jnam4o1r3NUk4otF9H6lGhd4zEt8mwAqBH9TRkeD9tsv/32s39AecQRR/APKdcJbeB8A6bNkcY10Ov2166xzlGNxqVztDcVa17nqCYVWy4ytE5zixJ9PMurKOf1rQNADehvyvApfULclNPTxsw3RNrQaFwDvW5/7RrrHNVoXDpHe1Ox5nWOalKx5SJD6zS3KNHHs7yKcl7fOgDUgP6mDJ/SJ8RNOT1tzHxDpA2NxjXQ6/bXrrHOUY3GpXO0NxVrXueoJhVbLjK0TnOLEn08y6so5/WtA0AN6G/K8Cl9QtyU09PGzDdE2tBoXAO9bn/tGusc1WhcOkd7U7HmdY5qUrHlIkPrNLco0cezvIpyXt86ANSA/qYMn9InxE05PW3MfEOkDY3GNdDr9teusc5Rjcalc7Q3FWte56gmFVsuMrROc4sSfTzLqyjn9a0DQA3ob8rwKX1C3JTT08bMN0Ta0GhcA71uf+0a6xzVaFw6R3tTseZ1jmpSseUiQ+s0tyjRx7O8inJe3zoA1ID+pgyf0ifETTk9bcx8Q6QNjcY10Ov2166xzlGNxqVztDcVa17nqCYVWy4ytE5zixJ9PMurKOf1rQNADehvyvApfULclNPTxkyH1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tD6zTXJ9pXIrWvNOdF61EOAJaJ/qYMn74nxE05PW3MdGhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8N7ROc32ifSVS+0pzXrQe5QBgmehvyvDpe0LclNPTxkyH1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tD6zTXJ9pXIrWvNOdF61EOAJaJ/qYMn74nxE05PW3MdGhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8N7ROc32ifSVS+0pzXrQe5QBgmehvyvDpe0LclNPTxkyH1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tD6zTXJ9pXIrWvNOdF61EOAJaJ/qYMn74nxE05PW3MdGhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8N7ROc32ifSVS+0pzXrQe5QBgmehvyvDpe0LclNPTxkyH1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tD6zTXJ9pXIrWvNOdF61EOAJaJ/qYMn74nxE05PW3MdGhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8F9XpnlyuT7SvRGpfac6L1qNczVLvB4D1g/6mDJ8KJ8RNOT174KeG1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tRne7J5fpE+0qk9pXmvGg9ytUs9X4AWD/ob8rwqXBC3JTTswd+amhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8F9XpnlyuT7SvRGpfac6L1qNczVLvB4D1g/6mDJ8KJ8RNOT174KeG1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tRne7J5fpE+0qk9pXmvGg9ytUs9X4AWD/ob8rwqXBC3JTTswd+amhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8F9XpnlyuT7SvRGpfac6L1qNczVLvB4D1g/6mDJ8KJ8RNOT174KeG1tZGr9eucUgcDaspnaO9qTiV1zjKaWw5y3tRne7J5fpE+0qk9pXmvGg9ytUs9X4AWD/ob8rwqXBC3JTTswd+amhtbfR67RqHxNGwmtI52puKU3mNo5zGlrO8F9XpnlyuT7SvRGpfac6L1qNczVLvB4D1g/6mDJ8KV+F1r3tds/POOzeXXHLJivwjH/nIZuPGjbfJG27K6dkDPzW0tjZ6vXaNQ+Lc0Nq+eMjQvRpHOY0176VqfOxzXl9sOc1rHEnt0+v0s+mLU7lWKj9UdI7mNM6J3g8A6wv9TRk+Fa7C8ccf382bNm2SlZ/ZY489NNXhppyeb3aiobW10eu1axwS54bW9sVDhu7VOMpprHkvVeNjn/P6YstpXuNIap9ep59NX5zKtVL5oaJzNKdxTvR+AFhf6G/K8KlwoGuvvba56KKLutcnn3yyrP7MAQccsCK+6aabupvxmmuu4aacmG92oqG1tdHrtWscEueG1vbFQ4bu1TjKaax5L1XjY5/z+mLLaV7jSGqfXqefTV+cyrVS+aGiczSncU70fgBYX2i6y/CpcKCtW7c2W7Zs6V4fe+yxsto0e+21l6ZoupfINzvR0Nra6PXaNQ6Jc0Nr++IhQ/dqHOU01ryXqvGxz3l9seU0r3EktU+v08+mL07lWqn8UNE5mtM4J3o/AKwvNN1l+FS4CieccEI377vvvivyf/EXf9F8/OMfX5HzuCmn55udaGhtbfR67RqHxLmhtX3xkKF7NY5yGmveS9X42Oe8vthymtc4ktqn1+ln0xencq1UfqjoHM1pnBO9HwDWF/qbMnwqXIUzzzyz2bBhQ3PxxRd38ebNm7t5u58+WWxEuCmnZw/81NDa2uj12jUOiXNDa/viIUP3ahzlNNa8l6rxsc95fbHlNK9xJLVPr9PPpi9O5Vqp/FDROZrTOCd6PwCsL/Q3ZfhUOCFuyun5ZicaWlsbvV67xiFxbmhtXzxk6F6No5zGmvdSNT72Oa8vtpzmNY6k9ul1+tn0xalcK5UfKjpHcxrnRO8HgPWF/qYMnwonxE05Pd/sREPrxjLWWXq9du6QODe0ti8eMnSvxlFOY817WqNDa3RvLracfuzSs7TO56JzfV0uzuU0r3EkqinJaZwTXdtY9FyN5+HPGvNcYD2ivynDp5IJcVNOzx74qaF1YxnrLL1eO3dInBta2xcPGbpX4yinseY9rdGhNbo3F1tOP3bpWVrnc9G5vi4X53Ka1zgS1ZTkNM6Jrm0seq7G8/BnjXkusB7R35ThU8mEuCmnZw/81NC6sYx1ll6vnTskzg2t7YuHDN2rcZTTWPOe1ujQGt2biy2nH7v0LK3zuehcX5eLcznNaxyJakpyGudE1zYWPVfjefizxjwXWI/ob8rwqWRC3JTTswd+amjdWMY6S6/Xzh0S54bW9sVDhu7VOMpprHlPa3Roje7NxZbTj116ltb5XHSur8vFuZzmNY5ENSU5jXOiaxuLnqvxPPxZY54LrEf0N2X4VDIhbsrp2QM/NbRuLGOdpddr5w6Jc0Nr++IhQ/dqHOU01rynNTq0RvfmYsvpxy49S+t8LjrX1+XiXE7zGkeimpKcxjnRtY1Fz9V4Hv6sMc8F1iP6mzJ8KpkQN+X07IGfGlo3lrHO0uu1c4fEuaG1ffGQoXs1jnIaa97TGh1ao3tzseX0Y5eepXU+F53r63JxLqd5jSNRTUlO45zo2sai52o8D3/WmOcC6xH9TRk+lUyIm3J69sBPDa0by1hn6fXauUPi3NDavnjI0L0aRzmNNe9pjQ6t0b252HL6sUvP0jqfi871dbk4l9O8xpGopiSncU50bWPRczWehz9rzHOB9Yj+pgyfSibETTk9e+CnhtaNZayz9Hrt3CFxbmhtXzxk6F6No5GqsbynNTq0JrXXYpU7T+t01jo9S/f4uiiO9mgutVf5vJ6Zeq1naaz6rs1LraXyntZE175aubM0HiK1N5VXfe8nsAz0N2X4qzshbsrp2QMqNbRuLGOdpddr5w6Jc0Nr++IhQ/dqHI1UjeU9rdGhNam9FqvceVqns9bpWbrH10VxtEdzqb3K5/XM1Gs9S2PVd21eai2V97QmuvbVyp2l8RCpvam86ns/gWWgvynDX90JcVNOzx5QqaF1YxnrLL1eO3dInBta2xcPGbpX42ikaizvaY0OrUnttVjlztM6nbVOz9I9vi6Koz2aS+1VPq9npl7rWRqrvmvzUmupvKc10bWvVu4sjYdI7U3lVd/7CSwD/U0Z/upOiJtyevaASg2tG8tYZ+n12rlD4tzQ2r54yNC9GkcjVWN5T2t0aE1qr8Uqd57W6ax1epbu8XVRHO3RXGqv8nk9M/Vaz9JY9V2bl1pL5T2tia59tXJnaTxEam8qr/reT2AZ6G/K8Fd3QtyU07MHVGpo3VjGOkuv184dEueG1vbFQ4bu1TgaqRrLe1qjQ2tSey1WufO0Tmet07N0j6+L4miP5lJ7lc/rmanXepbGqu/avNRaKu9pTXTtq5U7S+MhUntTedX3fgLLQH9Thr+6E+KmnJ49oFJD68Yy1ll6vXbukDg3tLYvHjJ0r8bRSNVY3tMaHVqT2muxyp2ndTprnZ6le3xdFEd7NJfaq3xez0y91rM0Vn3X5qXWUnlPa6JrX63cWRoPkdqbyqu+9xNYBvqbMvzVnRA35fTsAZUaWjeWsc7S67Vzh8S5obV98ZChezWORqrG8p7W6NCa1F6LVe48rdNZ6/Qs3eProjjao7nUXuXzembqtZ6lseq7Ni+1lsp7WhNd+2rlztJ4iNTeVF71vZ/AMtDflOGv7oS4KadnD6jU0LqxjHWWXq+dOyTODa3ti4cM3atxNFI1Pm+0RofWeJrXWHN9dTpHNTr8Hl8Xxbo3Oifa63PRx9RzfM5e+9loPlr3a7pueT8rzWsc5fTjak7zOqfqolpPY6P53Fm2Fu3RWWvmNfZ5uP2hvynDX7UJcVNOzz/IoqF1YxnrLL1eO3dInBta2xcPGbpX42ikanzeaI0OrfE0r7Hm+up0jmp0+D2+Lop1b3ROtNfnoo+p5/icvfaz0Xy07td03fJ+VprXOMrpx9Wc5nVO1UW1nsZG87mzbC3ao7PWzGvs83D7Q39Thr9qE+KmnJ5/kEVD68Yy1ll6vXbukDg3tLYvHjJ0r8bRSNX4vNEaHVrjaV5jzfXV6RzV6PB7fF0U697onGivz0UfU8/xOXvtZ6P5aN2v6brl/aw0r3GU04+rOc3rnKqLaj2NjeZzZ9latEdnrZnX2Ofh9of+pgx/1SbETTk9/yCLhtaNZayz9Hrt3CFxbmhtXzxk6F6No5Gq8XmjNTq0xtO8xprrq9M5qtHh9/i6KNa90TnRXp+LPqae43P22s9G89G6X9N1y/tZaV7jKKcfV3Oa1zlVF9V6GhvN586ytWiPzlozr7HPw+0P/U0Z/qpNiJtyev5BFg2tG8tYZ+n12rlD4tzQ2r54yNC9GkcjVePzRmt0aI2neY0111enc1Sjw+/xdVGse6Nzor0+F31MPcfn7LWfjeajdb+m65b3s9K8xlFOP67mNK9zqi6q9TQ2ms+dZWvRHp21Zl5jn4fbH/qbMvxVmxA35fT8gywaWjeWsc7S67Vzh8S5obV98ZChezWORqrG543W6NAaT/Maa66vTueoRoff4+uiWPdG50R7fS76mHqOz9lrPxvNR+t+Tdct72eleY2jnH5czWle51RdVOtpbDSfO8vWoj06a828xj4Ptz/0N2X4qzYhbsrp+QdZNLRuLGOdpddr5w6Jc0Nr++IhQ/dqHI1Ujc8brdGhNZ7mNdZcX53OUY0Ov8fXRbHujc6J9vpc9DH1HJ+z1342mo/W/ZquW97PSvMaRzn9uJrTvM6puqjW09hoPneWrUV7dNaaeY19Hm5/6G/K8FdtQtyU0/MPsmho3VjGOkuv184dEueG1vbFQ4bu1XjI0L0alwxP81HtanJRrLloaJ3GuaH7olwqr2dF5+qeKB+tRzUWR7PmUmdqztOPo8PyqTk6u+8M3edpPnWGX4v26Kw1li8R1UW5PrpHY9y+0N+U4a/JhLgpp+cfZNHQurGMdZZer507JM4Nre2Lhwzdq/GQoXs1Lhme5qPa1eSiWHPR0DqNc0P3RblUXs+KztU9UT5aj2osjmbNpc7UnKcfR4flU3N0dt8Zus/TfOoMvxbt0VlrLF8iqotyfXSPxrh9ob8pw1+TCXFTTs8/yKKhdWMZ6yy9Xjt3SJwbWtsXDxm6V+MhQ/dqXDI8zUe1q8lFseaioXUa54bui3KpvJ4Vnat7ony0HtVYHM2aS52pOU8/jg7Lp+bo7L4zdJ+n+dQZfi3ao7PWWL5EVBfl+ugejXH7Qn9Thr8mE+KmnJ5/kEVD68Yy1ll6vXbukDg3tLYvHjJ0r8ZDhu7VuGR4mo9qV5OLYs1FQ+s0zg3dF+VSeT0rOlf3RPloPaqxOJo1lzpTc55+HB2WT83R2X1n6D5P86kz/Fq0R2etsXyJqC7K9dE9GuP2hf6mDH9NJsRNOT3/IIuG1o1lrLP0eu3cIXFuaG1fPGToXo2HDN2rccnwNB/VriYXxZqLhtZpnBu6L8ql8npWdK7uifLRelRjcTRrLnWm5jz9ODosn5qjs/vO0H2e5lNn+LVoj85aY/kSUV2U66N7NMbtC/1NGf6aTIibcnr+QRYNrRvLWGfp9dq5Q+Lc0Nq+eMjQvRoPGbpX45LhaT6qXU0uijUXDa3TODd0X5RL5fWs6FzdE+Wj9ajG4mjWXOpMzXn6cXRYPjVHZ/edofs8zafO8GvRHp21xvIloroo10f3aIzbF/qbMvw1mRA35fT8gywaWjeWsc7S67Vzh8S5obV98ZChezUeMnSvxiXD03xUq7loaJ3GqVw0tE7jkmF7/F4T5XV/31lRXLrm16NZc31D6/2+1BlRrcZG92qt1gzJa86vRXmdfZ3J7TXRPstrrGcMmTXXZ+w6TI/+pgy38IS4KadnD4DU0LqxjHWWXq+dOyTODa3ti4cM3avxkKF7NS4ZnuajWs1FQ+s0TuWioXUalwzb4/eaKK/7+86K4tI1vx7NmusbWu/3pc6IajU2uldrtWZIXnN+Lcrr7OtMbq+J9lleYz1jyKy5PmPXYXr0N2W4hSfETTk9ewCkhtaNZayz9Hrt3CFxbmhtXzxk6F6Nhwzdq3HJ8DQf1WouGlqncSoXDa3TuGTYHr/XRHnd33dWFJeu+fVo1lzf0Hq/L3VGVKux0b1aqzVD8prza1FeZ19ncntNtM/yGusZQ2bN9Rm7DtOjvynDLTwhbsrp2QMgNbRuLGOdpddr5w6Jc0Nr++IhQ/dqPGToXo1Lhqf5qFZz0dA6jVO5aGidxiXD9vi9Jsrr/r6zorh0za9Hs+b6htb7fakzolqNje7VWq0ZktecX4vyOvs6k9tron2W11jPGDJrrs/YdZge/U0ZbuEJcVNOzx4AqaF1YxnrLL1eO3dInBta2xcPGbpX4yFD92pcMjzNR7Wai4bWaZzKRUPrNC4ZtsfvNVFe9/edFcWla349mjXXN7Te70udEdVqbHSv1mrNkLzm/FqU19nXmdxeE+2zvMZ6xpBZc33GrsP06G/KcAtPiJtyevYASA2tG8tYZ+n12rlD4tzQ2r54yNC9Gg8ZulfjkuFpPqrVXDS0TuNULhpap3HJsD1+r4nyur/vrCguXfPr0ay5vqH1fl/qjKhWY6N7tVZrhuQ159eivM6+zuT2mmif5TXWM4bMmuszdh2mR39Thlt4QtyU07MHQGpo3VjGOkuv184dEueG1vbFQ4bu1XjI0L0alwxP81Gt5qKhdRqnctHQOo1Lhu3xe02U1/19Z0Vx6Zpfj2bN9Q2t9/tSZ0S1Ghvdq7VaMySvOb8W5XX2dSa310T7LK+xnjFk1lyfseswPfqbMtzCE+KmnJ49AFJD68awiLP0mofEuaG1ffGQMc9eHXqWxkOG7tU4lYtGaV3J0LM0Xu0wUV5z846+M209mjXXN7RO49zI1RrN695UjeZz9bm1aL2vLsp5qXVfF9Xo8HuiWXOmL5/jz11LUtfs87k/W2otynnzrg9Ff1Nm5LcdOdyU07NPWKmhdWNYxFl6zUPi3NDavnjImGevDj1L4yFD92qcykWjtK5k6Fkar3aYKK+5eUffmbYezZrrG1qncW7kao3mdW+qRvO5+txatN5XF+W81Lqvi2p0+D3RrDnTl8/x564lqWv2+dyfLbUW5bx514eivykz8tuOHG7K6dknrNTQujEs4iy95iFxbmhtXzxkzLNXh56l8ZChezVO5aJRWlcy9CyNVztMlNfcvKPvTFuPZs31Da3TODdytUbzujdVo/lcfW4tWu+ri3Jeat3XRTU6/J5o1pzpy+f4c9eS1DX7fO7PllqLct6860PR35QZ+W1HDjfl9OwTVmpo3RgWcZZe85A4N7S2Lx4y5tmrQ8/SeMjQvRqnctEorSsZepbGqx0mymtu3tF3pq1Hs+b6htZpnBu5WqN53Zuq0XyuPrcWrffVRTkvte7rohodfk80a8705XP8uWtJ6pp9PvdnS61FOW/e9aHob8qM/LYjh5tyevYJKzW0bgyLOEuveUicG1rbFw8Z8+zVoWdpPGToXo1TuWiU1pUMPUvj1Q4T5TU37+g709ajWXN9Q+s0zo1crdG87k3VaD5Xn1uL1vvqopyXWvd1UY0OvyeaNWf68jn+3LUkdc0+n/uzpdainDfv+lD0N2VGftuRw005PfuElRpaN4ZFnKXXPCTODa3ti4eMefbq0LM0HjJ0r8apXDRK60qGnqXxaoeJ8pqbd/SdaevRrLm+oXUa50au1mhe96ZqNJ+rz61F6311Uc5Lrfu6qEaH3xPNmjN9+Rx/7lqSumafz/3ZUmtRzpt3fSj6mzIjv+3I4aacnn3CSg2tG8MiztJrHhLnhtb2xUPGPHt16FkaDxm6V+NULhqldSVDz9J4tcNEec3NO/rOtPVo1lzf0DqNcyNXazSve1M1ms/V59ai9b66KOel1n1dVKPD74lmzZm+fI4/dy1JXbPP5/5sqbUo5827PhT9TZmR33bkcFNOzz5hpYbWjWGes3SfXq+tD4lzQ2v74mUNvQ6Nhwzdq3Eqx+gffe+brvvYXmtNamidxqsdY51jo+S8VI3mNc7lLeel1nWv1ujQfHRWqkZz0Z5ItM+v9emrSa3rx+y7Vn+dWpuKNR+te1qv65ZPzbrf87GuGc23Mf1NmcRbikXgppye/wQTDa0bwzxn6T69XlsfEueG1vbFyxp6HRoPGbpX41SO0T/63jdd97G91prU0DqNVzvGOsdGyXmpGs1rnMtbzkut616t0aH56KxUjeaiPZFon1/r01eTWteP2Xet/jq1NhVrPlr3tF7XLZ+adb/nY10zmm9j+psyibcUi8BNOT3/CSYaWjeGec7SfXq9tj4kzg2t7YuXNfQ6NB4ydK/GqRyjf/S9b7ruY3utNamhdRqvdox1jo2S81I1mtc4l7ecl1rXvVqjQ/PRWakazUV7ItE+v9anrya1rh+z71r9dWptKtZ8tO5pva5bPjXrfs/HumY038b0N2USbykWgZtyev4TTDS0bgzznKX79HptfUicG1rbFy9r6HVoPGToXo1TOUb/6HvfdN3H9lprUkPrNF7tGOscGyXnpWo0r3Eubzkvta57tUaH5qOzUjWai/ZEon1+rU9fTWpdP2bftfrr1NpUrPlo3dN6Xbd8atb9no91zWi+jelvyiTeUiwCN+X0/CeYaGjdGOY5S/fp9dr6kDg3tLYvXtbQ69B4yNC9GqdyjP7R977puo/ttdakhtZpvNox1jk2Ss5L1Whe41zecl5qXfdqjQ7NR2elajQX7YlE+/xan76a1Lp+zL5r9deptalY89G6p/W6bvnUrPs9H+ua0Xwb09+USbylyNmwYUNz5ZVXNhs3blyR33HHHZvPfvazzR3ucIcVecNNOT3/CSYaWjeGec7SfXq9tj4kzg2t7YuXNfQ6NB4ydK/GqRyjf/S9b7ruY3utNamhdRqvdox1jo2S81I1mtc4l7ecl1rXvVqjQ/PRWakazUV7ItE+v9anrya1rh+z71r9dWptKtZ8tO5pva5bPjXrfs/HumY038b0N2USbylStm7d2mzZsqV7feyxx65YO+OMM7r5T//0T1fkb7rppu5m/O///u/mmmuumd2cjMWP7bbLD63T/asZ85yl+/R6bX1InBta2xcva+h1aDxk6F6NUzlG/+h733Tdx/Zaa1JD6zRe7RjrHBsl56VqNK9xLu/fTxupdd2rNTo0H52VqtFctMdfs9ZE61FOR19Nal0/Zt+1+uvU2lSs+Wg9+hj6WmtSs+6P9unrVI3FbW9z/fXXr+h9cFs03QNde+21zUUXXdS9Pvnkk1esveMd7+jms846a0X+lFNO+elNuR2DwWAwGAzGuhxt4408mu6BVvOVbiyP/S9xTI/3fnl475eH9355eO9RO5ruVdh5552779227+l+8Ytf3M077bRT87nPfS75Pd2YHp+El4f3fnl475eH9355eO9RO5ruVTjzzDO7f0x58cUXd/HmzZu7+R/+4R+6/HnnneeqsUzt99O3A9PjvV8e3vvl4b1fHt571I6mGwAAAFgwmm4AAABgwWi6sa7tt99+zcMf/nBNY0Snn356s/vuuzdPetKTZrnnPe95zW677dZ885vf7OKvfvWrza677tq84AUvmNVgPK94xSuaP/zDP+xe895P55nPfGazyy67NJ/4xCe6+E/+5E+6+Itf/GIXf+c732n22GOP5lnPepbfhhG89KUv7d7rl73sZV38k5/8pLn73e/ePO5xj5vVPOMZz2j22muv5oc//OEsBywTTTfWrXPPPbd505ve1Pze7/1ec9111+kyRnLkkUc2n/nMZ5rHP/7xzf/+7/92uXvd617NJz/5yebQQw/t4gc96EHNpZde2tz5znf2WzGS/ffff9Z0895P47vf/W5z3HHHNf/1X//VXHXVVV2ubfA+/elPN/e5z326+Nd//de7f/tz4IEH+q0YwZ3udKfmy1/+cvc/+FuvfOUrm3e/+93NE5/4xObGG2/scg95yEOaj3zkI83Tn/50vxVYGppurFvtbwg17SdiLNaXvvSl5oorrmg++MEPNt/73ve63L3vfe9ubh9+rbZB+dSnPjXbg/nZjy5tm27e++nc//73b57ylKc0D33oQ7v46quv7v7HTevRj350N9tPuLr55pubf/zHf/zZRoyi/X8xW3e96127uf050eb5z39+88Y3vnEW+2cBsEw03Vi3/CdhvsVk8ewh+Pa3v32W++Vf/uVuPuKII7r5Rz/6UXP++efP1jGf9rfctl9ZbbVNN+/9dPyPhj3kkEOaj33sY83Xv/71Lj7mmGO6+X73u9+s5uyzz569xvzuec97Npdffnmzzz77dLH/fP/Upz61efnLXz6L73KXu8xeA8tE0411i690T+f444/vvpLa4qut02l/UVd7n7dj++23b/7t3/6N934i9v62Nm3axFe6J/a6172um0877bRu5ivdWAtourFutd/Tfc455zTPfvazZ/+oDON77nOf21x44YXNN77xjeaGG27ocm1D0n5f8SMe8Ygubr+v+LLLLuMrTgtk39PNez+N//iP/+i+mtr+vwtve9vbulzbZLdfffXf033JJZc0P/dzP+e3YgT77rtv9z3d9m8V2u/pfs973tP9g277nu6DDz64+ehHP8r3dKMaNN0AAADAgtF0AwAAAAtG0w0AAAAsGE03AAAAsGA03QAAAMCC0XQDQMXan9BgP4puXvaz1D37kYIAgMWi6QaAirQ/Zq798YtPeMITVuQvuOCC2c/g9rkvfOELzYc//OHmAQ94wIq1HP8zjQEA0+AzLwBUpP05w63nPOc5za233jr7Sve73vWursG+/vrrZ7W+EW8b6fYXsJx11lnNq1/96uZDH/pQ8853vrP7LZTtz4pu2Ve629q2sW/ZV7r33HPP5vOf//zsNy22Nf/8z//c/arz9pe7AADmQ9MNABVpf3vebrvt1tzjHvfoYmu6U1/pbnPtrx9vf1nIoYceOlt7/OMf3zXfP/7xj2c533Qba7rt12bbr4+3miuvvLL53Oc+97NiAMCq0XQDQEXsK9233HJL85KXvKS36W5/tfsPfvCDLt57771na/ZbEd/73vc2d7/73bvmO9V0f//73+9+q2jrxBNPXFHTfsz24wAA5kPTDQAVse/pft7zntc1u9Z0f+1rX2vOOeec5oc//OGsVhvxLVu2NGeffXb3Fe527c1vfnNzxRVXNC996Uubb3/727Omu/215CXfXtKi6QaAcdB0A0BF2ma3HfZtHv6nl7Rfsd68efOsVpvu1gEHHNDc73736163TXjbTB9yyCFdbE13+9XvnXbaqXttTfepp57aNdz/8i//0sU03QAwLppuAAAAYMFougEAAIAFo+kGAAAAFoymGwAAAFgwmm4AAABgwWi6AQAAgAWj6QYAAAAWjKYbAAAAWDCabgAAAGDBaLoBAACABaPpBgAAABaMphsAAABYMJpuAAAAYMFougEAAIAFo+kGAAAAFuz/ACJ5Lk/40QBhAAAAAElFTkSuQmCC>