import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}
iterationNum = 0

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

#CHANGE THIS TO MAKE IT EITHER SMALL OR LARGE DATASET
def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def check_if_goal(node,target):
    return node.state[1] == target

def trace_path_back(node):
    path = []
    current_node = node
    #Base case if it's just one degree of seperation
    if current_node.parent is None:
        return [current_node.state]
    else:
        while current_node is not None:
            # Append the node's state to the path
            path.append(current_node.state)
            # print(path)
            # Go "backwards" in the chain to find the parent
            current_node = current_node.parent
        #Since going backwards in the chain, have to reverse the list
        # print(path)
        # print(len(path)//2 + 1)
        for i in range(len(path)//2):
            temp = path[i]
            path[i] = path[-1-i]
            path[-1-i] = temp
        return path

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    # TODO
    shortest_path_length = 0
    #Contains the people that have been explored already
    explored_list = []
    #The nodes to be explored, will use Breadth-first Search
    frontier = QueueFrontier()
    #Add nodes to the frontier, states are in this format --> (movie_id, person_id)
    # This will be the initial starting frontier
    for i in neighbors_for_person(source):
        frontier.add(Node(state=i, parent=None, action=None))
        if i[1] == target:
            break
    #frontier.remove() returns the node that was removed
    #Cycle through the frontier until it's empty
    path_to_target = [0]
    while not frontier.empty():
        #Look at the first element in the frontier (these are of the Node data type)
        #Remove the first node in the frontier
        current_node = frontier.remove()
        #print(trace_path_back(current_node))
        #print(frontier.elements())
        # If the node was already explored, just continue the program and don't do anything else
        continue_loop = False
        for explored in explored_list:
            #print(explored)
            #If node was already explored, no need to explore it further
            if explored == current_node.state and len(explored_list) != 0:
                continue_loop = True
                continue
        if continue_loop:
            continue
        # Add node to explored list by default
        explored_list.append(current_node.state)
        # Check if it's the goal node
        if check_if_goal(current_node, target) and len(trace_path_back(current_node)) <= 6:
            # By default set the first path, or if the length of the current path is longer than the new one found
            if path_to_target[0] == 0 and trace_path_back(current_node) is not None:
                path_to_target = trace_path_back(current_node)
            elif trace_path_back(current_node) != None:
                if len(path_to_target) > len(trace_path_back(current_node)) and trace_path_back(current_node) != None:
                    path_to_target = trace_path_back(current_node)
        # Check if it's actually worth looking for more nodes from the current node
        if len(trace_path_back(current_node)) < 6:
            if (len(trace_path_back(current_node)) + 1 < len(path_to_target) and path_to_target[0] != 0) or path_to_target[0] == 0:
                # Get movie list from the current node
                for z in neighbors_for_person(current_node.state[1]):
                    # Is this next node already in the frontier, or is it in the explored list?
                    # If it's either of these things, do not add it to the frontier
                    # Doing this b/c what's the point of adding a node that's been explored already
                    if not frontier.contains_state(z):
                        #By default add it to the frontier, unless there is stuff in the explored_list to check
                        add_to_frontier = True
                        for e in explored_list:
                            if z == e:
                                add_to_frontier = False
                                break
                        if add_to_frontier:
                                frontier.add(Node(state=z, parent=current_node, action=None))

    #If frontier is empty, this means there is no possible sol'n
    if frontier.empty() and path_to_target[0] == 0:
        return None
    else:
        return path_to_target
    raise NotImplementedError

#remember that when using QueueFrontier, it's first-in first out, so whatever entered list first is checked first


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
