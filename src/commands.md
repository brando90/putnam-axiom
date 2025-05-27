# Command to run with two GPUs

torchrun --nproc_per_node=2 --master_port=29500  ./putnam-axiom/src/contamination_ft.py   --deepspeed ./putnam-axiom/src/ds_config.json

