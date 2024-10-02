package main

// Import all the dependencies from the go.mod file
import (
	_ "github.com/go-task/slim-sprig"
	_ "github.com/go-task/slim-sprig/v3"
	_ "github.com/google/pprof"
	_ "github.com/onsi/ginkgo/v2"
	_ "github.com/quic-go/quic-go"
	_ "go.uber.org/mock"
	_ "golang.org/x/crypto"
	_ "golang.org/x/exp"
	_ "golang.org/x/mod"
	_ "golang.org/x/net"
	_ "golang.org/x/sync"
	_ "golang.org/x/sys"
	_ "golang.org/x/tools"
)

func main() {
	// The main function doesn't need to do anything.
	// We just need the imports for go mod tidy to recognize the dependencies.
}
