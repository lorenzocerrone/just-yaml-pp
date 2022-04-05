from yaml import nodes


def generic_constructor(loader, node, first_element=False):
    if isinstance(node, nodes.ScalarNode):
        return node.value

    elif isinstance(node, nodes.SequenceNode):
        seq = loader.construct_sequence(node)
        if first_element:
            seq = seq[0]
        return seq

    elif isinstance(node, nodes.MappingNode):
        return loader.construct_mapping(node)