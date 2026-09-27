from typing import Union, TYPE_CHECKING

from systemrdl.node import AddrmapNode, RootNode, MemNode
from systemrdl import builtin_udps
from systemrdl.properties.user_defined import ExternalUserProperty

from .rdl_generator import RDLGenerator

if TYPE_CHECKING:
    from systemrdl.messages import MessageHandler
    from systemrdl.node import Node

class SystemRDLExporter:
    msg: "MessageHandler"

    def export(self, node: Union[AddrmapNode, RootNode], path: str) -> None:
        self.msg = node.env.msg

        # If it is the root node, skip to top addrmap
        if isinstance(node, RootNode):
            node = node.top

        if not isinstance(node, (AddrmapNode, MemNode)):
            raise TypeError("'node' argument expects type AddrmapNode or MemNode. Got '%s'" % type(node).__name__)

        with open(path, 'w', encoding='utf-8') as f:
            if self._uses_builtin_udps(node):
                f.write(builtin_udps.get_rdl_declarations())
                f.write("\n")
            g = RDLGenerator()
            s = g.get_content(node)
            f.write(s)

    @staticmethod
    def _uses_builtin_udps(node: "Node") -> bool:
        """
        Built-in UDPs do not need to be declared, but the exported RDL declares
        them anyway so that it remains compilable by other SystemRDL tools.
        """
        user_properties = node.env.property_rules.user_properties
        names = {udp_cls.name for udp_cls in builtin_udps.ALL_BUILTIN_UDPS}
        for name in names:
            udp = user_properties.get(name)
            if isinstance(udp, ExternalUserProperty) and not udp.is_soft:
                return True
        for n in [node, *node.descendants()]:
            if names.intersection(n.list_properties(include_native=False)):
                return True
        return False
