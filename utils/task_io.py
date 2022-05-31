import json
from multiprocessing import Array
import numpy as np
import xml.etree.ElementTree as et
from typing import Dict, List, Tuple
from numpy.lib.stride_tricks import _sliding_window_view_dispatcher
import numpy.typing  as npt
from math import sqrt


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def save_task_to_json(file_name, positions, all_neighbours, a, s, t, size):
    fp = open(file_name, 'w')
    obj = {"graph": all_neighbours,
           "vert_positions": positions,
           "agents": a,
           "starts": s,
           "goals": t,
           "size": size}
    json.dump(obj, fp, indent=2,  cls=MyEncoder)


def read_task_from_json(file_name: str) -> Tuple[Dict[int, np.ndarray], Dict[int, List[int]], List[int], Dict[int, int], Dict[int, int], float]:
    '''
    Reads full information about task from JSON file 

    Parameters
    ----------
    file_name : str
        Full path of JSON file with task

    Returns
    -------
    positions : Dict[int, np.ndarray]: 
        Positions of vetices
    all_neighbours : Dict[int, List[int]]
        Dictionary with neighbours for every vertex
    agents : List[int]:
        List with id for every agents
    starts : Dict[int, int]
        Start vertices of agents
    goals : Dict[int, int]: 
        Goal vertices of agents
    size : float
        Radius of agents
    '''

    '''
    

    Args:
        file_name (str): 

    Returns:

    '''
    fp = open(file_name, 'r')
    task_dict = json.load(fp)

    pos_str = task_dict["vert_positions"]
    positions = dict()
    for v_id, v_pos in pos_str.items():
        positions[int(v_id)] = np.array(v_pos)

    all_neighbours_str = task_dict["graph"]
    all_neighbours = dict()
    for v_id, v_n in all_neighbours_str.items():
        all_neighbours[int(v_id)] = set(v_n)

    agents = task_dict["agents"]

    starts_str = task_dict["starts"]
    starts = dict()
    for a_id, v_id in starts_str.items():
        starts[int(a_id)] = v_id

    goals_str = task_dict["goals"]
    goals = dict()
    for a_id, v_id in goals_str.items():
        goals[int(a_id)] = v_id

    size = task_dict["size"]

    return positions, all_neighbours, agents, starts, goals, size


def save_task_to_xml(file_name, positions, all_neighbours, a, s, t, size):
    task_file_name = file_name + ".xml"
    root = et.Element('root')
    et.indent(root, space="\t", level=0)
    for a_i in a:
        agent = et.SubElement(root, 'agent')
        agent.set('start_id', str(s[a_i]))
        agent.set('goal_id', str(t[a_i]))
        et.indent(root, space="\t", level=0)

    tree = et.ElementTree(root)
    tree.write(task_file_name, xml_declaration=True, encoding='utf-8')

    map_file_name = file_name + "_map.xml"
    
    graphml = et.Element('graphml')
    graphml.set("xmlns", "http://graphml.graphdrawing.org/xmlns")
    graphml.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    graphml.set("xsi:schemaLocation", "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd")
    et.indent(graphml, space="\t", level=0)

    key0 = et.SubElement(graphml, "key")
    key0.set("id", "key0")
    key0.set("for", "node")
    key0.set("attr.name", "coords")
    key0.set("attr.type", "string")
    et.indent(graphml, space="\t", level=0)

    key1 = et.SubElement(graphml, "key")
    key1.set("id", "key1")
    key1.set("for", "edge")
    key1.set("attr.name", "weight")
    key1.set("attr.type", "double")
    et.indent(graphml, space="\t", level=0)

    graph = et.SubElement(graphml, "graph")
    graph.set("id", "G")
    graph.set("edgedefault", "directed")
    graph.set("parse.nodeids", "free")
    graph.set("parse.edgeids", "canonical")
    graph.set("parse.order", "nodesfirst")
    et.indent(graphml, space="\t", level=0)

    for node_id, position in positions.items():
        node = et.SubElement(graph, 'node')
        node.set('id', 'n'+str(node_id))
        et.indent(graphml, space="\t", level=0)
        data = et.SubElement(node, "data")
        data.set("key", "key0")
        data.text = str(position[0]) + "," + str(position[1])
        et.indent(graphml, space="\t", level=0)
        # et.indent(graphml, space="\t", level=0)

    edge_id = 0
    for node_id, neighbours in all_neighbours.items():
        for n_id in neighbours:
            edge = et.SubElement(graph, 'edge')
            edge.set('id', 'e'+str(edge_id))
            edge.set('source', 'n'+str(node_id))
            edge.set('target', 'n'+str(n_id))
            et.indent(graphml, space="\t", level=0)
            edge_id += 1
            data = et.SubElement(edge, "data")
            data.set("key", "key1")
            data.text = str(np.linalg.norm(positions[node_id] - positions[n_id]))
            et.indent(graphml, space="\t", level=0)
        # et.indent(graphml, space="\t", level=0)


    tree = et.ElementTree(graphml)
    tree.write(map_file_name, xml_declaration=True, encoding='utf-8')


def read_task_from_xml(map_file, task_file):
    
    tree = et.parse(map_file)
    root = tree.getroot()
    prefix = "{http://graphml.graphdrawing.org/xmlns}"

    graph = root.find(prefix+"graph")

    all_neighbours = dict()
    positions = dict()

    for node in graph.findall(prefix+"node"):
        node_id = int(node.attrib.get("id")[1:])
        node_coord = np.array(list(map(float, node.find(prefix+"data").text.split(","))))
        all_neighbours[node_id] = set()
        positions[node_id] = node_coord
        # print(node_id, node_coord)

    
    for edge in graph.findall(prefix+"edge"):
        v_from = int(edge.attrib.get("source")[1:])
        v_to = int(edge.attrib.get("target")[1:])
        all_neighbours[v_from].add(v_to)
        all_neighbours[v_to].add(v_from)

    
    tree = et.parse(task_file)
    root = tree.getroot()

    agents = list()
    starts = dict()
    goals = dict()
    
    
    for id, agent in enumerate(root.findall("agent")):
        agents.append(id)
        v_from = int(agent.attrib.get("start_id"))
        v_to = int(agent.attrib.get("goal_id"))
        starts[id] = v_from
        goals[id] = v_to

    size = sqrt(2)/4

    return positions, all_neighbours, agents, starts, goals, size


def read_xml_ccbs_results(result_file):
    tree = et.parse(result_file)
    root = tree.getroot()
    log = root.find("log")
    summary = log.find("summary")
    runtime = float(summary.attrib.get("time"))
    flowtime = float(summary.attrib.get("flowtime"))
    makespan = float(summary.attrib.get("makespan"))

    return runtime, flowtime, makespan