module_dir_abs="$(readlink -f ${PWD}/../tests/helpers/modules)"
export PYTHONPATH="${module_dir_abs}:${PYTHONPATH}"
echo ${PYTHONPATH}
