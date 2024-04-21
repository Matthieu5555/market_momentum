# MarketMomentum

#### Video Demo:  https://www.youtube.com/watch?v=UB6D6xsdCgY

#### Description:
This Python program analyzes trading volumes of stock tickers using data from Yahoo Finance. Users can select tickers from the S&P 500 or a CSV file, define a historical period for analysis, and specify a recent period to compare trading volumes. The program computes statistics like volume percentiles and Z-scores, identifies outliers, and augments the analysis with additional data such as P/E ratios and industry information. Results are displayed in a formatted table, highlighting stocks with significant volume changes. Note: This program is not a standalone financial analysis tool and should be used alongside sound valuation methods to guide user investment decisions.

#### Files:
The program can run independently but also accepts any CSV file provided it is located within the root folder of the application.

#### Process:
The development of MarketMomentum was inspired by the intersection of my CFA Level 1 studies and Yale's Financial Markets course, particularly the sections on behavioral finance. The idea was to create a tool to identify stocks gaining momentum from institutional investors—catching the wave right before retail investors pile in.

Initially, the application began as a CS50 project that simply listed the 10 most traded companies based on Z-scores a concept from my CFA studies. The user experience was basic, and automating the S&P 500 ticker list extraction was challenging.

Over time, the program evolved to spotlight "hot" and "cold" stocks based on median instead of mean calculations to avoid outlier bias. This provided more reliable results. User experience improvements followed, including features to load tickers from a CSV, select analysis periods, and even handle shorter periods where the central limit theorem is less applicable.

Further enhancements included a loading bar for better user interaction feedback, a clear startup banner, and a formatted results table with additional financial metrics like P/E ratios and industry data. To optimize performance, data fetching was refined to only retrieve additional metrics for stocks in the final table, significantly improving response times.

#### To do:
Future updates will focus on integrating live and hourly data to track intra-day momentum and identify emerging investment opportunities more dynamically. Add the capacity of restarting directly from the program. Add some FSA features.
