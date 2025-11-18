for i in {1..50}; do
  curl -s http://localhost/ > /dev/null &
  echo "Request $i sent"
done