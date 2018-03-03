NCBI MathML Schema

This copy of W3C MathML is identical to the version 2 distributed by
the W3 Consortium, with one change made for compatibility with the
NCBI schemas: its invocation of the XLink namespace schema (which
appears in the component common/common-attribs.xsd) has been adjusted
to point not to its bundled version of the XLink schema, but to the
version of XLink distributed for use with NCBI.

This is necessary because some schema processors cannot reconcile the
disparate invocations, despite the fact that the NCBI XLink is a clean
superset of the MathML XLink.

The normative version of MathML is available from

http://w3.org/Math/

