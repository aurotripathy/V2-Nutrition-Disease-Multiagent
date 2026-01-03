## Multi-Agent Nutrients/Disease System

#### YouTube Demo
[![Demo](https://img.youtube.com/vi/XIC1YOyzdLg/0.jpg)](https://www.youtube.com/watch?v=XIC1YOyzdLg)

The multi-agent system comprises a:
- nutrients discovery agent and a
- disease analysis agent based on the nutrients discovered. 

These two agents collaborate using the 'sequential' pattern from the ADK.

### Fun Fact
The nutrient discovery agent deploys an LLM with tool-calling capabilities to access the Open Food Facts (OFF) database with a text-search API.

In some cases, the API returns a Nova number. The Nova classification is a framework for grouping edible substances based on the extent and purpose of food processing applied to them. Researchers at the University of São Paulo, Brazil, proposed the system in 2009.

Nova classifies food into four groups and assigns the number below (1 is healthy, 4 is unhealthy):

1. Unprocessed or minimally processed foods
2. Processed culinary ingredients
3. Processed foods
4. Ultra-processed foods



