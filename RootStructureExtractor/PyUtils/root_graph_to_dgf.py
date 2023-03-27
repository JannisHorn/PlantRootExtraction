import numpy as np
import math
import root_graph
from copy import deepcopy


def rescaleNode( node, mults ):
    x, y, z = node.getCoor()
    return [x *mults[0], y *mults[1], z *mults[2]]

def dfs_tree(root, node_idx, node_list, seg_list, dim_mults):  # node_idx is the index of root

    for child in root:
        # get the coordinates
        child = root_graph.c_graph.CGraphNode( child )
        #print(child.getCoor())
        #x, y, z = child.getCoor()
        x,y,z = rescaleNode( child, dim_mults )
        child_rad = child.getRad()
        child_idx = node_list[-1][0] + 1
        node_list.append([child_idx, x, y, z])

        branch_id = child.getBranchId()
        seg_list.append([node_idx, child_idx, branch_id,
                         child_rad])  # node1ID, node2ID, order, brnID, surf [cm2], length [cm], radius [cm], kz [cm4 hPa-1 d-1], kr [cm hPa-1 d-1], emergence time [d], subtype, organtype

        if len(child) != 0:  # if not leaf node, recursively call this function
            dfs_tree(child, child_idx, node_list, seg_list, dim_mults)  # branch id needs to be updated

    return node_list, seg_list


def generate_node_seg_lists(root, dim_mults):
    node_idx = 0
    x, y, z = rescaleNode(root, dim_mults)
    node_list = [[node_idx, x, y, z]]
    seg_list = []  # node1ID, node2ID, brnID, radius [cm]

    # apply depth first search on the tree structure of the root graph
    node_list, seg_list = dfs_tree(root, node_idx, node_list, seg_list, dim_mults)

    return node_list, seg_list


def set_LenSur(vertex, prev, nodeID, radius):
    """
    use the dfs order to calculate emergence time
    :param vertex: the list of node coordinates
    :param prev: the list of segment start nodes
    :param nodeID: the list segment end nodes
    :param radius: the list of segment radii
    :return: 
    """
    length = np.zeros(len(prev))
    surf = np.zeros(len(prev))

    for i in range(0, len(prev)):
        a = vertex[int(prev[i]), :]
        b = vertex[int(nodeID[i]), :]
        length[i] = np.linalg.norm(a - b)
        surf[i] = 2 * radius[i] * math.pi * length[i]

    return length, surf


def set_type(branchID, prev):
    """
    Starting from type 1, the successor of branches with type i will be assigned with type i+1
    """

    # maxbran = int(max(branchID))
    un_bran = np.unique(branchID)  # unique branches: 0 removed, because the 0 branch only contains the first node
    un_bran = np.asarray(un_bran, int)
    maxbran = len(un_bran)  # number of unique branches

    preseg = np.zeros(maxbran)
    prebr = np.zeros(maxbran)
    for i in range(1, maxbran + 1):
        # res = next(x for x, val in enumerate(branchID) if val == i)  # index of every 1st branch segment
        res = next(x for x, val in enumerate(branchID) if val == un_bran[i-1])  # index of every 1st branch segment
        preseg[i - 1] = int(prev[res]) - 1  # prvious of first br seg
        # print(un_bran[i-1], res, int(prev[res]), branchID[int(prev[res])-1])

    preseg = np.array(preseg, int)
    prebr = branchID[preseg]  ### the branch id of the parent branch of each branch
    prebr[0] = 0

    # find branch types
    branch_type = np.zeros(len(prebr))
    idx = np.where(prebr == 0)
    branch_type[idx[0]] = 1  # the type of main branch is 1

    for i in range(1, len(un_bran)):  # the largest possible branch type is the number of unique branches
        bridx = np.where(branch_type == i)  # index of branches with type i
        dumpre = un_bran[bridx[
            0]]  # num of branches that have type i # To me it's more like the branchID of the branches of type i
        if len(dumpre) == 0:
            break  # once there's no succeeding branches, stop the iteration
        idxpre = np.in1d(prebr, dumpre)  # the child branches whose parent branches are of type i
        branch_type[idxpre] = i + 1

    # distribute branch types on all segments
    Order = np.zeros(len(branchID))
    Order[np.where(branchID == 0)[0]] = 1  # the first segment of the main branch is of type 1
    for i in range(len(un_bran)):
        #　idx = np.where(un_bran == i)
        # tt = branch_type[idx[0]]  # get the branch type of this branch id
        tt = branch_type[i]  # get the branch type of this branch id
        # ix = np.where(branchID == i)
        ix = np.where(branchID == un_bran[i])
        Order[ix[
            0]] = tt  # Q: only the 1st seg of the branch is changed? --> no, ix[0] is the result array, ix is a tuple

    return Order


def set_age(Order, branchID, prev, length, maxage, minage):
    '''
    Modified algorithm:
    Use the orders (types) of branches to calculate the emergence time of each branch 
      (start time is 0 for the first segment of the main branch, and each branch tip ends at maxage)
    The emergence time of the next order branches (the next level of child branches) will be calculated 
      based on the time tag of the current branches
    '''
    un_typ = np.unique(Order)
    emt = np.zeros(len(Order)) + minage  # emergence time

    for i in range(1, len(un_typ) + 1):
        idx = np.where(Order == i)  # find all segments with this order
        brtyp = np.unique(branchID[idx[0]])  # find unique branch IDs with this order

        for j in range(0, len(brtyp)):  # iterate through all branchIDs with this order
            idx1_ = np.where(branchID == brtyp[j])
            idx1 = np.asarray(idx1_[0], int)
            emt[idx1[0]] = emt[int(prev[idx1[0]])]
            emt[idx1[-1]] = maxage  # tip is set to maxage
            iniage = emt[idx1[0]]
            RL = sum(length[idx1])  # length of this whole branch
            agediff = (maxage - iniage);
            if (agediff != 0):
                elong = RL / (maxage - iniage)
            else:
                elong = 0.0001

            for k in range(1, len(idx1) - 1):
                emt[idx1[k]] = emt[idx1[k - 1]] + length[idx1[k]] / elong

    # convert the age into unit of day (to integer)
    emt = emt.astype(int)

    return emt


def set_max_type(order, maxtyp):
    """
    Set the max order/type: Any order larger than the max order will be converted to the max order
    """
    order[order > maxtyp] = maxtyp
    un_typ = np.unique(order)

    return order


def write_dgf(filename, nodes, seg, params=np.zeros((0, 0))):
    file = open(filename, "w")  # write file

    nop = params.shape[0]  # number of parameters
    file.write("DGF\n")
    file.write('Vertex\n')
    file.write('parameters 0\n')

    for i in range(0, len(nodes)):
        file.write('{:g} {:g} {:g} \n'.format(nodes[i, 0], nodes[i, 1], nodes[i, 2]))

    file.write('#\n');
    file.write('Simplex\n');
    if nop > 0:
        file.write('parameters {:d}'.format(nop))
        file.write(': node1ID, node2ID, order, brnID, surf [cm2], length [cm], radius [cm], kz [cm4 hPa-1 d-1], '
                   'kr [cm hPa-1 d-1], emergence time [d], subtype, organtype \n');
    for i in range(0, seg.shape[1]):
        file.write('{:g} {:g}'.format(seg[0, i], seg[1, i]))
        for j in range(0, nop):
            file.write(' {:g}'.format(params[j, i]))
        file.write(' \n')

    # not used...
    file.write('#\nBOUNDARYSEGMENTS\n2 0\n')
    file.write('3 {:g}\n'.format((seg.shape[1])))
    file.write('#\nBOUNDARYDOMAIN\ndefault 1\n#\n')
    file.close()


def graph_to_dgf(root_graph, min_plant_age, max_plant_age, max_type, dgf_output_path, voxel_resolution, dim_mults):
    """
    The function that converts root graph to dgf format and write it in a file
    voxel_resolution should be in the unit of µm / voxel!
    """
    voxel_resolution *= 1000
    print( "Params: minage={}, maxage={}, maxtype={}, voxel_res={}".format(min_plant_age, max_plant_age, max_type, voxel_resolution) )
    node_list, seg_list = generate_node_seg_lists(root_graph.getRoot(), dim_mults)
    node_list = np.array(node_list)
    seg_list = np.array(seg_list)

    # set the root origin node to (0,0,0), and subtract the offset from other nodes too
    _, origin_x, origin_y, origin_z = node_list[0, :]
    node_list[:, 1] -= origin_x
    node_list[:, 2] -= origin_y
    node_list[:, 3] -= origin_z

    # convert the node coordinates to length in centimeter
    node_list = node_list.astype(float)
    node_list[:, 1:] *= voxel_resolution / (10 ** 4)

    # convert the radius to length in centimeter
    seg_list[:, 3] *= voxel_resolution / (10 ** 4)

    # calculate the length and surface of each segment
    vertex = node_list[:, 1:]
    prev, nodeID, branchID, radius = seg_list[:, 0], seg_list[:, 1], seg_list[:, 2], seg_list[:, 3]
    length, surf = set_LenSur(vertex, prev, nodeID, radius)

    # calculate the order of each branch segment
    order = set_type(branchID, prev)

    # calculate the emergence time
    emt = set_age(order, branchID, prev, length,
                  max_plant_age, min_plant_age)  # maximum age of this palnt = 13, shall be given by the user

    # set the max type
    order = set_max_type(order, max_type)

    # combine segments and parameters
    seg = (np.stack((prev, nodeID)))
    kz = np.zeros(emt.shape)
    kr = np.zeros(emt.shape)
    subtype = deepcopy(order)
    organtype = np.zeros(emt.shape)  # ?
    params = (np.stack((order, branchID, surf, length, radius, kz, kr, emt, subtype, organtype)))

    # convert the node coordinates from centimeter to meter
    #vertex /= 10 ** 2

    # write the dgf file:
    write_dgf(dgf_output_path, vertex, seg, params)

    return


if __name__ == '__main__':
    # parameters needed
    some_path_of_graph_xml = ''
    output_path_of_dgf = ''
    max_plant_age = 12
    min_plant_age = 0
    max_type = 3
    voxel_resolution = 60

    # load the root graph and convert ot dgf
    rg = root_graph.RootGraph(some_path_of_graph_xml)
    graph_to_dgf(rg, min_plant_age, max_plant_age, max_type, output_path_of_dgf, voxel_resolution)



