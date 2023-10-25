import bpy
bl_info = {
    "name": "Node counter - N面板",
    "description": "Counts all nodes in active node tree",
    "author": "原作者:Vladan Trhlík; 大量修改:一尘不染",
    "blender": (2, 80, 0),
    "version" : (1, 3, 0),
    "category": "Node",
}

def count_in_tree(tree, nodes_count, nodes_include_count, include_group=True, only_select=False):
    count_include_group = 0
    count_exclude_group = 0
    groups_count = 0
    groups_counted = []

    counts = {"总节点数量-含组内": count_include_group, "总节点数量-不含组内": count_exclude_group, 
                "节点组数量-不重复": len(groups_counted), "节点组数量-重复": groups_count}
    if only_select:
        nodes = tree
    else:
        nodes = [node for node in tree.nodes]
    # for node in tree.nodes:
    for node in nodes:
        count_include_group += 1
        count_exclude_group += 1
        # nodes
        name = node.name.split(".")[0]
        if name == "Group":
            name = "Node Group"
        # 下面 if else 不能缩进,缩进就只有name == "Group"才会运行了
        if name not in nodes_count:
            nodes_count[name] = 1
        else:
            nodes_count[name] += 1

        # groups
        if include_group:
            if name == 'Node Group':
                groups_count += 1
                if node.node_tree.name not in nodes_include_count:
                    nodes_include_count[node.node_tree.name] = {"groups_count": 1, "group_node_count":len(node.node_tree.nodes)}
                else:
                    nodes_include_count[node.node_tree.name]["groups_count"] += 1

            # if name == 'Node Group' and node.node_tree not in groups_counted:
            if name == 'Node Group':       # 这样统计当前节点树重复节点累积节点数量
                if node.node_tree not in groups_counted:
                    groups_counted.append(node.node_tree)
                count_include_group += count_in_tree(node.node_tree, nodes_count, nodes_include_count)["总节点数量-含组内"]
                
    counts = {"总节点数量-含组内": count_include_group, "总节点数量-不含组内": count_exclude_group, 
              "节点组数量-不重复": len(groups_counted), "节点组数量-重复": groups_count }
    return counts

def count_in_tree2(tree, nodes_include_count):
# def count_in_tree2(tree, nodes_count, nodes_include_count, only_select=False):
    for node in tree.nodes:
        node_name = node.name.split(".")[0]
        # node_name = node.name.split()
        
        if node_name == 'Group':
            tree_name = node.node_tree.name
            if tree_name not in nodes_include_count:
                # count_in_tree(tree, nodes_count, nodes_include_count, only_select=True)
                # count += count_in_tree(node.node_tree)
                count = len(node.node_tree.nodes)
                nodes_include_count[tree_name] = {"groups_count": 1, "group_node_count": count}
            else:
                nodes_include_count[tree_name]["groups_count"] += 1


class Node_PT_0(bpy.types.Panel):
    bl_label = '节点数量'
    bl_idname = 'Node_PT_0'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = '节点树'
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        layout = self.layout

class Node_PT_0_0(bpy.types.Panel):
    bl_label = '节点树节点数量总览'
    bl_idname = 'Node_PT_0_0'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_order = 0
    bl_parent_id = 'Node_PT_0'

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        nodes_count = {}
        nodes_include_count = {}
        node_tree = context.space_data.edit_tree
        counts = count_in_tree(node_tree, nodes_count, nodes_include_count)

        layout = self.layout
        main_box = layout.box()
        split = main_box.split(factor=0.6)
        split.label(text="节点树名字")
        
        tree_name = node_tree.name
        if context.area.ui_type == "ShaderNodeTree":
            tree_name = context.space_data.id.name
        split.label(text=tree_name)
        split = main_box.split(factor=0.6)
        split.label(text="总节点数量-含组内")
        split.label(text=str(counts["总节点数量-含组内"]))
        split = main_box.split(factor=0.6)
        split.label(text="总节点数量-不含组内")
        split.label(text=str(counts["总节点数量-不含组内"]))
        split = main_box.split(factor=0.6)
        split.label(text="节点组数量-重复")
        split.label(text=str(counts["节点组数量-重复"]))
        split = main_box.split(factor=0.6)
        split.label(text="节点组数量-不重复")
        split.label(text=str(counts["节点组数量-不重复"]))

class Node_PT_0_1(bpy.types.Panel):
    bl_label = '节点详细数量-不含节点组内'
    bl_idname = 'Node_PT_0_1'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_order = 1
    bl_parent_id = 'Node_PT_0'

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        nodes_count = {}
        nodes_include_count = {}
        node_tree = context.space_data.edit_tree
        counts = count_in_tree(node_tree, nodes_count, nodes_include_count, include_group=False)        # 函数会修改传递进去的空字典,运行函数就行

        node_exclude = self.layout.box()
        split = node_exclude.split(factor=0.6)
        split.label(text="总数")
        split.label(text=str(counts["总节点数量-不含组内"]))
        for key, item in sorted(nodes_count.items(), key = lambda kv:(kv[1], kv[0]), reverse=True):
            split = node_exclude.split(factor=0.6)
            split.label(text=key)
            split.label(text=str(item))

class Node_PT_0_2(bpy.types.Panel):
    bl_label = '节点详细数量-含节点组内'
    bl_idname = 'Node_PT_0_2'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_order = 2
    bl_parent_id = 'Node_PT_0'

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        nodes_count = {}
        nodes_include_count = {}
        node_tree = context.space_data.edit_tree
        counts = count_in_tree(node_tree, nodes_count, nodes_include_count)

        node_include = self.layout.box()
        split = node_include.split(factor=0.6)
        split.label(text="总数")
        split.label(text=str(counts["总节点数量-含组内"]))
        for key, item in sorted(nodes_count.items(), key = lambda kv:(kv[1], kv[0]), reverse=True):
            split = node_include.split(factor=0.6)
            split.label(text=key)
            split.label(text=str(item))

class Node_PT_0_3(bpy.types.Panel):
    bl_label = '节点组重复次数及各节点组内节点数量'
    bl_idname = 'Node_PT_0_3'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_order = 3
    bl_parent_id = 'Node_PT_0'

    @classmethod
    def poll(cls, context):
        return not (False)

    def draw(self, context):
        nodes_count = {}
        nodes_include_count = {}
        node_tree = context.space_data.edit_tree
        # counts = count_in_tree(node_tree, nodes_count, nodes_include_count)
        count_in_tree2(node_tree, nodes_include_count)        # 函数会修改传递进去的空字典,运行函数就行
        # print(nodes_include_count)
        # count_in_tree2(node_tree, nodes_count, nodes_include_count, include_group=True)
        group_include = self.layout.box()
        for key, item in sorted(nodes_include_count.items(), key = lambda x:x[1]['group_node_count'], reverse=True):
            # row = group_include.row()
            split = group_include.split(factor=0.6)
            split.label(text=key)
            split.label(text=str(item["groups_count"]) + " | " + str(item["group_node_count"]))

class Node_PT_0_4(bpy.types.Panel):
    bl_label = '选定节点数量-包含节点组内'
    bl_idname = 'Node_PT_0_4'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_order = 0
    bl_parent_id = 'Node_PT_0'

    def draw(self, context):
        nodes_count = {}
        nodes_include_count = {}
        node_tree = context.selected_nodes
        counts = count_in_tree(node_tree, nodes_count, nodes_include_count, only_select=True)

        node_include = self.layout.box()
        split = node_include.split(factor=0.6)
        split.label(text="总数")
        split.label(text=str(counts["总节点数量-含组内"]))
        for key, item in sorted(nodes_count.items(), key = lambda kv:(kv[1], kv[0]), reverse=True):
            split = node_include.split(factor=0.6)
            split.label(text=key)
            split.label(text=str(item))


classes = [Node_PT_0,
           Node_PT_0_0,
           Node_PT_0_1,
           Node_PT_0_2,
           Node_PT_0_3,
           Node_PT_0_4,
           ]
def register():
    for i in classes:
        bpy.utils.register_class(i)

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
