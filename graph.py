from logging import getLogger
log = getLogger('nate')

def neighbors(planets):
    planets = [p for p in planets]
    N = len(planets)
    dist = [[float('inf') for j in range(N)] for i in range(N)]
    marks = {} # Which machines are being used for which moves

    # Modified Floyd-Warshall algorithm keeps track of the best way
    # to get from all i to any j. Note that this will remove all
    # strongly dominated edges and repeated emages

    for source in planets:
        i = planets.index(source)
        for dest in planets:
            j = planets.index(dest)
            dist[i][j] = source.distance(dest)
            marks[i, j] = [j]

    for k in range(N):
        for i in range(N):
            for j in range(N):
                if i == j: continue
                old = dist[i][j]
                new = dist[i][k] + dist[k][j]
                if new < old: marks[i, j] = marks[i, k] + marks[k, j]
                dist[i][j] = min(old, new)

    neighbors = {}
    for (s, d) in marks:
        source = planets[s]
        dest = planets[d]
        path = ' '.join(str(planets[i].id) for i in marks[s, d])
        log.debug('Shortest path %s to %s is: %s' % (source.id, dest.id, path))
        nearby = neighbors.setdefault(source, set())
        nearby.add(planets[marks[s, d][0]])
    return neighbors
