# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
""" Neighborhood objects """

import numpy as N
from numpy import array
import operator
import sys

from mvpa.clfs.distance import cartesianDistance

class Sphere(object):
    """ 3 Dimensional sphere

    Use this if you want to obtain all the neighbors within a given diameter of
    a 3 dimensional coordiante.

    Example
    -------
    Create a Sphere of diamter 9 and obtain all coordinates within range for the
    coordinate (1,1,1).

    >>> s = Sphere(9)
    >>>coords = s((1,1,1))

    """
    def __init__(self, diameter, extent=(sys.maxint, sys.maxint, sys.maxint)):
        """ Initialise the Sphere

        Parameters
        ----------
        diameter : odd int
            diameter of the sphere in voxels
        extent :  sequence of 3 ints
            maximum index to consider
            if this is not provided it will be the maximum value of an integer

        """
        self.extent = N.asanyarray(extent)
        if __debug__:
            if diameter%2 != 1:
                raise ValueError("Sphere diameter must be odd, but is: %d"
                                % diameter)
            if len(self.extent) != 3 \
                or self.extent.dtype.char not in N.typecodes['AllInteger']:
                raise ValueError("Sphere extent must be 3 integers, was: %s"
                                % type(extent))
        self.diameter = diameter
        self.radius = diameter/2
        self.coord_list = self._create_template()
        self.dataset = None

    def _create_template(self):
        center = array((0,0,0))
        lr = range(-self.radius,self.radius+1) # linear range
        # TODO create additional distance metrics, for example manhatten
        # TODO create a way to specify shape of quantised sphere i.e. < vs <=
        return array([array((i,j,k)) for i in lr
                              for j in lr
                              for k in lr
                              if cartesianDistance(array((i,j,k)),center)
                                 <= self.radius])

    def train(self, dataset):
        # XXX techincally this is not needed
        self.dataset = dataset

    def __call__(self, coordinate):
        """  Get all coordinates within diameter

        Parameters
        ----------
        coordinate : sequence type of length 3 with integers

        """
        # type checking
        coordinate = N.asanyarray(coordinate)
        if __debug__:
            if len(coordinate) != 3 \
            or coordinate.dtype.char not in N.typecodes['AllInteger']:
                raise ValueError("Sphere must be called on a sequence of integers of "
                                 "length 3, you gave: "+ str(coordinate))
            #if dataset is None:
            #    raise ValueError("Sphere object has not been trained yet, use "
            #                     "train(dataset) first. ")
        # function call
        coord_array = (coordinate + self.coord_list)
        # now filter out illegal coordinates if they really are outside the
        # bounds
        if (coordinate - self.radius < 0).any() \
        or (coordinate + self.radius >= self.extent).any():
            coord_array = array([c for c in coord_array \
                                   if (c >= 0).all()
                                   and (c < self.extent).all()])

        coord_array = coord_array.transpose()
        return zip(coord_array[0], coord_array[1], coord_array[2])


class QueryEngine(object):
    """ XXX Please document me """
    def __init__(self, **kwargs):
        # XXX for example:
        # space=Sphere(diameter=3)
        self.spaces_to_objects = kwargs
        self.spaces_to_fcoord = {}

    def train(self, dataset):
        self.ds = dataset

    def __call__(self, feature_id):
        """ for a given feature id get the local neighborhood in all spaces"""
        # XXX check for untrained
        for space, neighborhood_object in self.spaces_to_objects.items():
            # lookup the coordinate of the feature
            coord = self.ds.fa[space].value[feature_id]
            # obtain the coordinates in the neighborhood of the faeture
            # using the neighborhood object for this space
            feature_coord = neighborhood_object(coord)
            # store the feature coordinates for later siftig
            self.spaces_to_fcoord[space] = feature_coord
        # now that we have collected the coordinates for each space
        # do the siftig via the mapper

        #XXX This needs a refactoring, since get_outids() is no longer part of
        #mappers ( this is not a comment 
        raise NotImplementedError
        return self.ds.mapper.get_outids([], **self.spaces_to_fcoord)

