from __future__ import division
import time
import math
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import config_user as gl
import all_functions as fcn

# Create local copies of constants
sizeX, sizeY, sizeZ, zMove = gl.sizeX, gl.sizeY, gl.sizeZ, gl.sizeX * gl.sizeY
rXstart, rYstart, rZstart, rXdim, rYdim, rZdim = gl.rXstart, gl.rYstart, gl.rZstart, gl.rXdim, gl.rYdim, gl.rZdim




# Check user inputs
fcn.clusterDimCheck()


# Add moving goals to goals array
if gl.initX:
    newgoals = np.zeros((len(gl.initX), 4))
    for w in xrange(0, len(gl.initX)):
        newgoals[w, 0] = gl.initX[w]
        newgoals[w, 1] = gl.initY[w]
        newgoals[w, 2] = gl.initZ[w]
    gl.goals = np.vstack((gl.goals, newgoals))

gl.numGoals = gl.goals.shape[0]


hyp = []
for i in xrange(0, gl.numGoals):
    gX, gY, gZ = gl.goals[i, 0], gl.goals[i, 1], gl.goals[i, 2]
    xdist, ydist, zdist = gX - gl.start[0], gY - gl.start[1], gZ - gl.start[2]
    hyp.append(math.sqrt(xdist**2 + ydist**2 + zdist**2))

goalindex = hyp.index(min(hyp))
gl.goal = (gl.goals[goalindex, 0], gl.goals[goalindex, 1], gl.goals[goalindex, 2])


# Ensure start coordinate are valid
if gl.start[0]>sizeX or gl.start[1]>sizeY or gl.start[2]>sizeZ or gl.start[0]<1 or gl.start[1]<1 or gl.start[2]<1:
    raise ValueError('Start coordinates are outside of map_ boundary')


# Add node number and cantor id to goals array
hyp = []
for i in xrange(0, gl.numGoals):
    gX, gY, gZ = gl.goals[i, 0], gl.goals[i, 1], gl.goals[i, 2]
    gl.goals[i, 3] = fcn.cantor(gX, gY, gZ)

gl.goal = (gl.goals[goalindex,0], gl.goals[goalindex,1], gl.goals[goalindex,2])



# Generating random fixed obstacles
np.random.seed(gl.seedStatic)
randomint = np.random.random_integers
obs_append = gl.obstacles.append
for i in xrange(0, gl.num2gen):
    newXFixed, newYFixed, newZFixed = randomint(1, sizeX), randomint(1, sizeY), randomint(1, sizeZ)

    obsnode = (newXFixed, newYFixed, newZFixed)
    # Don't place obstacle at start, goal, other obstacles, or within searchRadius
    if obsnode == gl.start:
        continue
    if obsnode in gl.goals or obsnode == gl.goal:
        continue

    curX, curY, curZ = gl.start
    if max([abs(curX - newXFixed),abs(curY - newYFixed),abs(curZ - newZFixed)]) < gl.searchRadius:
        continue
    newObsArray = (newXFixed, newYFixed, newZFixed)

    obs_append(newObsArray)
    # if len(gl.obstacles) > 0:
    #     gl.obstacles = np.vstack((gl.obstacles, newObsArray))
    # else:
    #     gl.obstacles = np.array(newObsArray)

"""

# Update map with obstacle coordinates, and update cost matrices such that cells
#   with obstacles have cost of infinity
#
# 0   = Open space
# 1   = UAV (not used)
# 2   = Goal (not used)
# -1  = Obstacle
# -2  = Newly detected / undetected obstacle

"""

# Generate plot with start and goal nodes
if gl.makeFigure:
    gl.goalhandles = {}
    gl.ax1.scatter(gl.start[0], gl.start[1], gl.start[2], c='g')
    for idx,eachgoal in enumerate(gl.goals):
        # This is done to save and remove scatter points for moving goals
        q = eachgoal[-1]
        gl.goalhandles[q] = gl.ax1.scatter(eachgoal[0], eachgoal[1], eachgoal[2], c='r')

    # Plot individual obstacles
    for idx, obs in enumerate(gl.obstacles):
        fcn.plotRectObs(obs[0], obs[1], obs[2], 1, 1, 1, 0.2, gl.ax1)


# Plot rectangular obstacles and them to obstacles array
for i in xrange(0,len(rXstart)):
    # if i == 2:  # skip this obstacle for now
    #     continue

    # Define each pair of x,y,z coordinates. Each column is a vertex
    if gl.makeFigure:
        fcn.plotRectObs(rXstart[i], rYstart[i], rZstart[i], rXdim[i], rYdim[i], rZdim[i], 0.2, gl.ax1)

    rLoc = fcn.rectObs(rXdim[i], rYdim[i], rZdim[i], rXstart[i], rYstart[i], rZstart[i])

    gl.obstacles.extend(rLoc)
    # if len(gl.obstacles) > 0:
    #     gl.obstacles = np.vstack((gl.obstacles, rLoc))
    # else:
    #     gl.obstacles = np.array(rLoc)
gl.number_of_obstacles = len(gl.obstacles)


# Update cost matrix if needed
for obsLoc in gl.obstacles:
    #obsLoc = (obs[0], obs[1], obs[2])
    if gl.startWithEmptyMap:
        gl.map_[obsLoc] = -2                     # mark as undetected obstacle
    elif not gl.startWithEmptyMap:
        gl.map_[obsLoc] = -1                     # mark as known obstacle
        gl.costMatrix[obsLoc] = float('inf')
        for obsSucc in fcn.succ(obsLoc):
            gl.map_[obsLoc] = -1                     # mark as known obstacle
            gl.costMatrix[obsLoc] = float('inf')


    else:
        raise ValueError('\'startWithEmptymap\' must be equal to True or False')


# Configure plot settings
xMin, xMax = 0.5, sizeX+0.5
yMin, yMax = 0.5, sizeY+0.5
zMin, zMax = 0.5, sizeZ+0.5
if gl.makeFigure:
    gl.ax1.set_xlabel('x'), gl.ax1.set_ylabel('y'), gl.ax1.set_zlabel('z')
    gl.ax1.set_xlim(xMin, xMax), gl.ax1.set_ylim(yMin, yMax), gl.ax1.set_zlim(zMin, zMax)
    gl.ax1.view_init(elev=44., azim= -168)
    gl.ax1.locator_params(axis='z',nbins=6)

    """
    Scaling for plot is done from here...
    """
    x_scale=sizeX
    y_scale=sizeY
    z_scale=sizeZ

    scale=np.diag([x_scale, y_scale, z_scale, 1.0])
    scale *= (1.0/scale.max())
    scale[3,3]=1.0

    def modified_proj():
      return np.dot(Axes3D.get_proj(gl.ax1), scale)

    gl.ax1.get_proj=modified_proj
    """
    to here
    """

# Determine number of levels
gl.numlevels = 1 # at least the one original level and one abstract level
maxdim = max(sizeX, sizeY, sizeZ)
while maxdim > gl.minclustersize:
    maxdim /= 4
    gl.numlevels += 1
