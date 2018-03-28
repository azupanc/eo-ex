# Earth Observation Examples

Repository for Earth Observation examples with resources. 

## Water Level Monitor

Aim of this example is to monitor water levels in large manmade or natural water reservoirs, dams, lakes, etc from space. The example shows how to build a simple water detector based on Normalized Difference Water Index and Otsu’s adaptive threshold method. In the example the water detection is applied to a:
* single Sentinel-2 scene of a dam,
* all Sentinel-2 scenes of a dam to get evolution of water levels through history,
* and all water bodies (several hundred) in South Africa to show how the method can be easily scaled to a country, a continent, or even the entire globe.

The water level in this example is estimated by taking the ratio of reservoirs’ current water surface area and water surface area when reservoir is full.

Read more about it at [this blog](https://medium.com/sentinel-hub/global-earth-observation-service-from-your-laptop-23157680cf5e).