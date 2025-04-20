Basically I want to just fo the following:
1) Use GEANT TOPOLOGY.
2) Have some producers, have some consumers.
3) II will generate traffic that has timestamp, consumer, domain, record type, log (a boolean whether to log the result or not)
4) We will ignore the timestamp and now one by one just make the requests for this traffic.
5) What I want to measure the average time for response for all the traffic. Basically for one traffic generated, one average time. Then this can be done multiple times to get the dtandard deviation.
6) Then we can also chanage the alpha parameter in the traffic generation to such experiment again, just like in icarus.
7) And I want to do something similar but for DNS also so we can show comparison betwwn NDN-DNS and DNS.

Contents in the folder:
1) In tests, there is a simple-test.py file in which I am making a small experiment with three nodes connected in triangel. a node is a consumer and b and c nodes are producers. 
2) First I run the server-conf-gen.py script to make the server confs for the ndn-traffic-generator server for each domain and store in server-configs. But the configs Ii have generated are wrong I guess, The format I did is not working I guess. So Copilot did some changes directly in the simple-test.py script. But still it doesn't work.
3) You will need the ndn-traffic-generator repo.
