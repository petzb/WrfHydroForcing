#!/usr/bin/env python

import argparse
import sys
import netCDF4

"""
Script to perform a conversion between gr3 file and ESMF Unstructured Grid Format

Example Usage:  ./gr3_2_esmf.py hgrid.gr3 hgrid.nc
"""


class gr3:
    """
    A class to store and investigate hgrid.gr3 data files
    """
    def __init__(self,filename,num_elem,num_nodes):
        self.filename = filename
        self.num_elem = int(num_elem)
        self.num_nodes = int(num_nodes)
        self.lons = [-9999.0]*self.num_nodes
        self.lats = [-9999.0]*self.num_nodes
        self.elevs = [-9999.0]*self.num_nodes
        self.elems = [[]]*self.num_elem

    def max_elem_len(self):
        return max(self.elem_lens())

    def elem_lens(self):
        return [len(elem) for elem in self.elems]

    def padded_elems(self,pad_val=-1):
        max_elem_len = self.max_elem_len()
        return [elem + [pad_val]*(max_elem_len-len(elem)) for elem in self.elems]

    def __str__(self):
        return "filename: %s\nnum_elements: %d\nnum_nodes: %d\nlons: \n%s\nlats: \n%s\nelevs: \n%s\nelem_nodes:\n%s" % (self.filename, self.num_elem, self.num_nodes, ",\n".join("%.4f" % lon for lon in self.lons),",\n".join("%.4f" % lat for lat in self.lats),",\n".join("%.4f" % elev for elev in self.elevs),",\n".join("%s" % elem for elem in self.elems))


def parse_gr3_file(gr3_input):
    """
    Parses a .gr3 file

    gr3 format:
    Line 1: File name (this line is ignored by the model)
    Line 2: Number of elements, Number of nodes
    Line 3 - Line (Number of nodes+2): Node number, longitude, latitude, elevation
    Next line - Number of elements: Element number, number of nodes in element, list of nodes that make up element
    The last section lists the open ocean and land boundary nodes.
    """
    gr3_obj = None
    with open(gr3_input) as f:
        filename = f.readline().rstrip()
        num_elem, num_nodes = f.readline().split()
        gr3_obj = gr3(filename,num_elem,num_nodes)
        for i in range(gr3_obj.num_nodes):
            node_num, lon, lat, elev = f.readline().split()
            gr3_obj.lons[i] = float(lon)
            gr3_obj.lats[i] = float(lat)
            gr3_obj.elevs[i] = float(elev)
        for i in range(gr3_obj.num_elem):
            elem_num,node_count,*node_lst = f.readline().split()
            gr3_obj.elems[i] = list(map(lambda x: int(x)-1,node_lst))
        
    return gr3_obj


def write_nc_mesh(gr3_obj,esmf_output):
    """
    Writes an hgrid.gr3 object to netcdf in the ESMF unstructured mesh format

    ESMF unstructured grid:
    https://earthsystemmodeling.org/docs/release/ESMF_8_0_1/ESMF_refdoc/node3.html#SECTION03028200000000000000
    """
    nc = netCDF4.Dataset(esmf_output, "w", format="NETCDF4")
    
    node_count_dim = nc.createDimension("nodeCount", gr3_obj.num_nodes)
    elem_count_dim = nc.createDimension("elementCount", gr3_obj.num_elem)
    max_elem_len = gr3_obj.max_elem_len()
    max_node_pe_elem_dim = nc.createDimension("maxNodePElement", max_elem_len)
    node_count_dim = nc.createDimension("coordDim", 2)
    
    node_coords_var = nc.createVariable("nodeCoords","f8",("nodeCount","coordDim"))
    node_coords_var.units = "degrees"
    elem_conn_var = nc.createVariable("elementConn","i",("elementCount","maxNodePElement"),fill_value=-1)
    elem_conn_var.long_name = "Node Indices that define the element connectivity"
    elem_conn_var.start_index = 0
    num_elem_conn_var = nc.createVariable("numElementConn","b","elementCount")
    num_elem_conn_var.long_name = "Number of nodes per element"
    ##Non-required Variables
    # center_coords_var = nc.createVariable("centerCoords","f8",("elementCount","coordDim"))
    # center_coords_var.units = "degrees"
    # elem_area_var = nc.createVariable("elementArea","f8","elementCount")
    # elem_area_var.units = "radians^2"
    # elem_area_var.long_name = "area weights"
    # elem_mask_var = nc.createVariable("elementMask","i","elementCount",fill_value=-9999.)
    nc.gridType = "unstructured"
    nc.version = "0.9"

    node_coords_var[:,0] = gr3_obj.lons
    node_coords_var[:,1] = gr3_obj.lats
    elem_conn_var[:] = gr3_obj.padded_elems() 
    num_elem_conn_var[:] = gr3_obj.elem_lens() 
    
    nc.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('gr3_input',type=str,help='Input .gr3 file')
    parser.add_argument('esmf_output',type=str,help='Output ESMF .nc file')
    args = parser.parse_args()
    gr3_obj = parse_gr3_file(args.gr3_input)
    print(gr3_obj)    
    write_nc_mesh(gr3_obj,args.esmf_output)


if __name__ == '__main__':
    main()
