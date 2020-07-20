# Build the container
docker build -t tdw:v1.6.0 .

# Set render target for virtualgl
DISPLAY=:0

# Allow x server to accept local connections
xhost +local:root

# Start virtual display for xpra
xpra start :80

# Set render target of virtual display (xpra) 
DISPLAY=:80

# Allow xpra x server to accept local connections
xhost +local:root

# Run the container
docker run -it \
  --rm \
  --gpus all \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  --network host \
  vglrun -d :0 \
  tdw:1.6.0 \
  ./TDW/TDW.x86_64
