from dimension import m1s_medium, m1d_medium

dimension_nodes = {
"m1s_no_oversubscription" : {
    "vCPU" : 2,
    "memory" : 8,
    "cpu_oversubscription" : 2,
    "memory_oversubscription" : 1,
    "node" : m1s_medium,
    "alias" : "m1s"
    }
,
"m1s_oversubscription" : {
    "vCPU" : 2,
    "memory" : 8,
    "cpu_oversubscription" : 3,
    "memory_oversubscription" : 1.25,
    "node" : m1s_medium,
    "alias" : "m1s_o"
    }
,
"m1d_no_oversubscription" : {
    "vCPU" : 2,
    "memory" : 8,
    "cpu_oversubscription" : 2,
    "memory_oversubscription" : 1,
    "node" : m1d_medium,
    "alias" : "m1d"
    }
,
"m1d_oversubscription" : {
    "vCPU" : 2,
    "memory" : 8,
    "cpu_oversubscription" : 3,
    "memory_oversubscription" : 1.25,
    "node" : m1d_medium,
    "alias" : "m1d_o"
    }
}