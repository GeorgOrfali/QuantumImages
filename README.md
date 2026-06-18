# QuantumImages

This Repository simulates the execution time  for Images beeing represented and encrypted in a Quantum Cluster state on Distributed and Non-Distributed Environments, with also the research for the effects on Noise and decoherence.

The official Thesis name was: Execution time Analysis of Quantum circuits in Distributed and Non-Distributed Environments for Image Encoding and Encryption.

# Image Encoding and Encryption Algorithm in Qiskit

## Encoding Algorithm 
<img width="585" height="100" alt="grafik" src="https://github.com/user-attachments/assets/9ce4e4be-3ac0-40ff-bc56-b61627601ce5" />

For example the Encoding Algorithm would look like this on the circuit:
<img width="973" height="430" alt="grafik" src="https://github.com/user-attachments/assets/ca4a44bf-e6a5-42ed-a5ef-b0ec5f47882d" />

## Encryption Algorithm
<img width="1023" height="93" alt="grafik" src="https://github.com/user-attachments/assets/859a916e-e7bc-4634-bbd0-c1c6973782f5" />

For example the Encryption Algorithm would look like this on the circuit:
<img width="991" height="468" alt="grafik" src="https://github.com/user-attachments/assets/433a1550-150d-42da-bbef-5250277e6bed" />


## Source for the Algorithm
Arijit Mandal, Shreya Banerjee, and Prasanta K. Panigrahi. “Quantum Image
Representation on Clusters.” In: 2021 IEEE International Conference on Quantum
Computing and Engineering (QCE). 2021 IEEE International Conference
on Quantum Computing and Engineering (QCE). Oct. 2021, pp. 89–99. doi:
10.1109/QCE52317.2021.00025.

# Distributed Algorithm
## Sequential Circuit Distribution
### Theoretical Concept
<img width="999" height="694" alt="grafik" src="https://github.com/user-attachments/assets/c72c039e-d4f0-420f-a3ac-4a1eed1880b6" />


### Source
Felix Burt, Kuan-Cheng Chen, and Kin Leung. Generalised Circuit Partitioning
for Distributed Quantum Computing. Aug. 2, 2024. arXiv: 2408.01424[quant-ph].
url: http://arxiv.org/abs/2408.01424 (visited on 09/27/2024).

## Parallel Circuit Distribution
### Theoretical Concept
<img width="687" height="967" alt="grafik" src="https://github.com/user-attachments/assets/7f26dbfe-a4f5-4b23-bfea-8f9a51be23c7" />


### Source

1. Wei Tang, Teague Tomesh, Martin Suchara, Jeffrey Larson, and Margaret Martonosi.
“CutQC: using small Quantum computers for large Quantum circuit evaluations.”
In: Proceedings of the 26th ACM International Conference on Architectural
Support for Programming Languages and Operating Systems. ASPLOS ’21: 26th
ACM International Conference on Architectural Support for Programming Languages
and Operating Systems. Virtual USA: ACM, Apr. 19, 2021, pp. 473–486. isbn: 978-1-4503-8317-2. doi: 10 . 1145 / 3445814 . 3446758. url: https://dl.acm.org/doi/10.1145/3445814.3446758 (visited on 09/17/2024).

2. Rodney Van Meter,W. J. Munro, Kae Nemoto, and Kohei M. Itoh. “Arithmetic on
a Distributed-Memory Quantum Multicomputer.” In: ACM Journal on Emerging
Technologies in Computing Systems 3.4 (Jan. 2008), pp. 1–23. issn: 1550-4832,
1550-4840. doi: 10 . 1145 / 1324177 . 1324179. arXiv: quant - ph / 0607160. url:
http://arxiv.org/abs/quant-ph/0607160 (visited on 08/19/2024).

# Start the simulation
After pulling the code you can just use these simple make commands to run it.
## Set Up
Before installing we need to check the Python version: 3.7.15 (this was tested on)
Then just use the command 

`
make setup
` 
to install all dependencies with pip

## Run
To Run the simulation just use the command 
`
make run
`

## Error
If an error occurs when executing the run command then try

`
make clean
`
