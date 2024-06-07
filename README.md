# Dash + Mito Medium Article App

<div align="center">
  <a href="https://dash.plotly.com/project-maintenance">
    <img src="https://dash.plotly.com/assets/images/maintained-by-plotly.png" width="400px" alt="Maintained by Plotly">
  </a>
</div>


Imagine you're a data scientist at a hedge fund. Your organization asked you to help the traders **track and visualize Tesla's stock over time in comparison to the S&P 500**.
You are given two datasets --one that shows Tesla stock activity over time, and one that shows S&P Market activity over time.

You need to build an app that lets your analysts:
1.  Upload two datasets
2.  Merge them together
3.  Create pivot tables to analyze the data
4.  Create graphs to visualize trends and key metrics from both datasets 

This GitHub repo implements two apps that achieve this objective.
1. `app.py` is a dynamic dash application built from scratch using Python to ETL, merge, and visualize your data.
2. `app-mito.py` is a dynamic dash application that uses **[Mito](https://www.trymito.io)** to to ETL, merge, and visualize your data.

Achieving your organization's objective is possible with either approach, but as a less-technical user, these apps hope to highlight how Mito lowers the barrier to entry into the Python data application ecosystem.

### Run this app locally

1. Install the required dependencies
```
pip install -r requirements.txt
```

2. Run the Dash app **without Mito**
```
python app.py
```

3. Run the Dash app **with Mito**
```
python app-mito.py
```

4. Follow the instructions in the terminal to view the app in your browser.

### Questions? Comments? Feedback?
Mito is a new Dash component. We'd love to hear your feedback and suggestions for improvement. 
1. Open an issue on the Mito for Dash [GitHub repo](https://github.com/mito-ds/mito)
2. Email the Mito for Dash maintainers: nate [at] sagacollab [dot] com
