# Written by scripts/lvs_top.py: the PDK setup, then the changes below.
source {/foss/pdks/ihp-sg13g2/libs.tech/netgen/ihp-sg13g2_setup.tcl}
# the Monte Carlo switch mm_ok of the Xschem netlists does not describe the layout
foreach c [cells list -all -circuit1] { catch {property "-circuit1 $c" delete mm_ok} }
foreach c [cells list -all -circuit2] { catch {property "-circuit2 $c" delete mm_ok} }
# layout cells without devices
catch {ignore class "-circuit1 RM_IHPSG13_1P_DEC_LE_l0wire"}
catch {ignore class "-circuit1 RM_IHPSG13_1P_DEC_LE_l1wire"}
catch {ignore class "-circuit1 RM_IHPSG13_1P_DEC_LE_l2wire"}
# from flow/lvs/config.yaml
foreach d {rppd rsil rhigh} { catch {property "-circuit2 $d" delete r} }
