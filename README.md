# Evaluation of Decisions on Interventions using Interactive and Animated Uncertainty-Aware Visualizations of Simulated Data
## Data and Analysis Code of the User Study 

Analysis framework for the evaluation user study of the simulated interventions' data visualizations.

- **analysis.ipynb**            : statistical analysis of participants' accuracy, response times, and confidence using Bayesian analysis
- **demographics.ipynb**        : demographic statistics of participants
- **descriptive_stats.ipynb**   : various data (not statistical) analyses and visualizations of the collected data
- **randomness_analysis.ipynb** : comparison of participants' responses with the responses simulated from ideal random agents

The data collected from the user study can be found in **data/study_02.db**. It is provided in the form of a sql database. The data can be accessed using the methods in **utils/db/get_data_db.py**.

The PyMC3 code for the Bayesian probabilistic models used for the analysis can be found in **utils/models.py**.
