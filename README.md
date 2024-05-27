# PLUS_Software_Dev_ClimateDataProject
## Tasks:
- [ ] taking a look into the libraries (meteostat/geopanda/folium) (all)
  - [ ] try to get the example code from github running until
- [ ] data analysis (entry level: all, advanced: tbd)
- [ ] visualize data (entry level: all, advanced: tbd)
- [ ] documentation

### Done:
- [x] Proposal delivery (all)
  - [x] Contribute to the proposal up to 9.5. (Deadline (!) is 10.5., 23:59)
     
### Suspended
- [ ] QGIS plugin (tbd)
- [ ] GUI (tbd)

### Meeting May 27th
- QGIS may be too much work and too far off the intended purpose of the project (for now!). Suspended until we know the progress.
- Polar Coordinate Visualisation is basically understood, but wind speed aggregation still produces some issues (aggregation frames? means? sums?)

#### meteostat data queries:
	daily -  query only one month
	monthly - query only one year

- wind data (vector calculus?)
	- how is that usually handled?

- one region, different stations, for now:  30 closest stations, add distance filter?

- Github:
  actually collaborate! 
  	pull before working, push after working
  	common environment: David will set up a .yaml for the basic environment that covers most stuff. Use it!



# Brainstorming
Let us start with a brainstorming of what might be possible/cool/interesting/... Feel free to add whatever you want:
- Use meteostat to import climate/weather data to python (https://github.com/meteostat/meteostat-python)
- visualize weather data in a map/time series plot
- take a look into geopanda and folium
- qgis plugin
- simple weather forecast
- compare different places
- compare different times for one place
- visualize climate change on a map/time series plot
- compare monthly/seasonal data
- gui (?)
