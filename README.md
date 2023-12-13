# distributed_causal_discovery


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- PROJECT LOGO -->
<br />

<h3 align="center">Distribted Causal Discovery</h3>

  <p align="center">
    Parallelized Causal Inference
    <br />
    <a href="https://github.com/Zhylkaaa/distributed_causal_discovery"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Zhylkaaa/distributed_causal_discovery">View Demo</a>
    ·
    <a href="https://github.com/Zhylkaaa/distributed_causal_discovery/issues">Report Bug</a>
    ·
    <a href="https://github.com/Zhylkaaa/distributed_causal_discovery/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
We provide a framework for running the Peter-Clark (PC) algorithm in a paralellized fashion
<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Installation

Clone the repo onto your machine
   ```sh
   git clone (https://github.com/Zhylkaaa/distributed_causal_discovery)
   ```
This repository was run and tested with python 3.8 and 3.9, in case of any issues please open contact us by opening the issue on github.
To install dependencies run:
```bash
python -m pip install -r requirements.txt
```

### Data processing

To obtain data please first run:
```bash
bash scripts/download_data.sh
```

this should take a few seconds. After that you can run:
```bash
python preprcessing/preprocess_pems_data.py
```
Look into the source code to find how you can customize parameters of processing.
By default, script produces subsampled version of dataset with `20` nodes and applies non-overlapping sliding window of size `2` 


<!-- USAGE EXAMPLES -->
## Usage

To use this code, simply clone the repository and run the following script - altering the parameters as necessary
   ```sh
   sbatch launch_ray.sh path_to_gt_graph <4> <32>
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Run experiments

To establish baseline results run:
```bash
time python run_baseline.py
```

In order to start distributed experiment on slurm cluster use:
```bash
sbatch launch_ray_job.sh data/gt_pems_graph_2_20.pkl <cpus for weak actor> <cpus for strong actor>
```
or locally with:
```bash
time PYTHONPATH=.:$PYTHONPATH python -u methods/constraint_based/pc.py data/gt_pems_graph_2_20.pkl <cpus for weak actor> <cpus for strong actor>
```


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions or suggestions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Dmytro Zhylko - dz2449@nyu.edu, Baraa Al Jorf - baj321@nyu.edu

Project Link: https://github.com/Zhylkaaa/distributed_causal_discovery

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-url]: https://github.com/Zhylkaaa/distributed_causal_discovery/graphs/contributers
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[forks-shield]: https://img.shields.io/github/forks/BaraaaALJorf/Jetbot_Linefollowing.svg?style=for-the-badge
[forks-url]: https://github.com/BaraaAlJorf/Jetbot_Linefollowing//network/members
