# Versions and changelog information

## 0.0.6

Exposed arbitrary configuration for product and builds

* additional-configurations added to product configurations
* additional-configurations added to build configurations

## 0.0.5

* Remove conditionals around loop; we will always loop through the builds once
* Enable short name to be prepended to undefined brew ref and package names
* Default 0th build name to project name
* Prevent components from nudging themselves

## 0.0.4

* Allow skipping nudges for a component when leveraging default nudges

## 0.0.3

* Allow release-type customizations

## 0.0.2

* Add ability to specify default owners on a project level
* Smarter loops in template pre-processing

## 0.0.1

Initial release -- no more force-pushing to override what was and now isn't