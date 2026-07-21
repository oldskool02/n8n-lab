

run_version() {
    echo "===================================="
    echo " Operations Toolkit"
    echo "===================================="
    echo

    echo "Project : $PROJECT_NAME"
    echo "Author  : $PROJECT_AUTHOR"
    echo "Version : $(cat "$VERSION_FILE")"
}
