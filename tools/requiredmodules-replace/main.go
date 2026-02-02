package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io"
	"os"
	"path/filepath"
)

const (
	defaultSearch  = "Vietnam Assets Pack by EightBall & Tobi"
	defaultReplace = "[VWV] Vietnam Assets Pack"
)

func usage() {
	fmt.Fprintf(os.Stderr,
		"Usage: %s <input.miz> <output.miz> [search] [replace]\n",
		os.Args[0],
	)
	os.Exit(1)
}

// Replace only inside requiredModules = { ... }
func replaceInRequiredModules(data []byte, find, replace string) ([]byte, bool) {
	start, end, ok := findRequiredModulesTable(data)
	if !ok {
		return data, false
	}

	block := data[start : end+1]
	newBlock := bytes.ReplaceAll(block, []byte(find), []byte(replace))
	if bytes.Equal(block, newBlock) {
		return data, false
	}

	out := make([]byte, 0, len(data)-len(block)+len(newBlock))
	out = append(out, data[:start]...)
	out = append(out, newBlock...)
	out = append(out, data[end+1:]...)

	return out, true
}

func main() {
	if len(os.Args) < 3 || len(os.Args) > 5 {
		usage()
	}

	inMiz := os.Args[1]
	outMiz := os.Args[2]

	find := defaultSearch
	replace := defaultReplace

	if len(os.Args) < 4 {
		fmt.Println("Using default search string:", defaultSearch)
		fmt.Println("Using default replace string:", defaultReplace)
	}

	if len(os.Args) >= 4 {
		find = os.Args[3]
	}
	if len(os.Args) == 5 {
		replace = os.Args[4]
	}

	inPath, err := filepath.Abs(inMiz)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error resolving input path:", err)
		os.Exit(1)
	}

	outPath, err := filepath.Abs(outMiz)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error resolving output path:", err)
		os.Exit(1)
	}

	if inPath == outPath {
		fmt.Fprintln(os.Stderr, "Error: input and output .miz must be different files.")
		os.Exit(1)
	}

	r, err := zip.OpenReader(inMiz)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error opening input:", err)
		os.Exit(1)
	}
	defer r.Close()

	out, err := os.Create(outMiz)
	if err != nil {
		fmt.Fprintln(os.Stderr, "Error creating output:", err)
		os.Exit(1)
	}
	defer out.Close()

	w := zip.NewWriter(out)
	defer w.Close()

	replaced := false

	for _, f := range r.File {
		if f.FileInfo().IsDir() {
			h := f.FileHeader
			if _, err := w.CreateHeader(&h); err != nil {
				fmt.Fprintln(os.Stderr, "Error creating zip entry:", err)
				os.Exit(1)
			}
			continue
		}

		rc, err := f.Open()
		if err != nil {
			fmt.Fprintln(os.Stderr, "Error reading file:", f.Name, err)
			os.Exit(1)
		}
		data, err := io.ReadAll(rc)
		rc.Close()
		if err != nil {
			fmt.Fprintln(os.Stderr, "Error reading file:", f.Name, err)
			os.Exit(1)
		}

		if f.Name == "mission" {
			var changed bool
			data, changed = replaceInRequiredModules(data, find, replace)
			replaced = replaced || changed
		}

		h := f.FileHeader
		wr, err := w.CreateHeader(&h)
		if err != nil {
			fmt.Fprintln(os.Stderr, "Error creating zip entry:", err)
			os.Exit(1)
		}
		if _, err := wr.Write(data); err != nil {
			fmt.Fprintln(os.Stderr, "Error writing zip entry:", err)
			os.Exit(1)
		}
	}

	if replaced {
		fmt.Println("Replacement done in requiredModules.")
	} else {
		fmt.Println("Warning: no replacement made (requiredModules or search string not found).")
	}

	fmt.Println("Output written to:", outMiz)
}

func findRequiredModulesTable(data []byte) (int, int, bool) {
	key := []byte("requiredModules")
	for i := 0; i < len(data); {
		if next, skipped := skipNonCode(data, i); skipped {
			i = next
			continue
		}

		if isKeyAt(data, i, key) {
			j := i + len(key)
			j = skipSpaceAndComments(data, j)
			if j < len(data) && data[j] == '=' {
				j++
				j = skipSpaceAndComments(data, j)
				if j < len(data) && data[j] == '{' {
					end, ok := findMatchingBrace(data, j)
					if ok {
						return j, end, true
					}
				}
			}
		}

		i++
	}

	return 0, 0, false
}

func isKeyAt(data []byte, i int, key []byte) bool {
	if i+len(key) > len(data) {
		return false
	}
	if !bytes.Equal(data[i:i+len(key)], key) {
		return false
	}
	if i > 0 && isIdentChar(data[i-1]) {
		return false
	}
	if i+len(key) < len(data) && isIdentChar(data[i+len(key)]) {
		return false
	}
	return true
}

func isIdentChar(b byte) bool {
	return b == '_' ||
		(b >= 'a' && b <= 'z') ||
		(b >= 'A' && b <= 'Z') ||
		(b >= '0' && b <= '9')
}

func skipSpaceAndComments(data []byte, i int) int {
	for i < len(data) {
		switch data[i] {
		case ' ', '\t', '\n', '\r':
			i++
			continue
		}

		if i+1 < len(data) && data[i] == '-' && data[i+1] == '-' {
			if next, ok := skipLongComment(data, i); ok {
				i = next
				continue
			}
			i = skipLineComment(data, i+2)
			continue
		}

		break
	}

	return i
}

func skipNonCode(data []byte, i int) (int, bool) {
	if i >= len(data) {
		return i, false
	}

	if i+1 < len(data) && data[i] == '-' && data[i+1] == '-' {
		if next, ok := skipLongComment(data, i); ok {
			return next, true
		}
		return skipLineComment(data, i+2), true
	}

	if data[i] == '"' || data[i] == '\'' {
		return skipShortString(data, i, data[i]), true
	}

	if data[i] == '[' {
		if next, ok := skipLongBracket(data, i); ok {
			return next, true
		}
	}

	return i, false
}

func skipShortString(data []byte, i int, quote byte) int {
	i++
	for i < len(data) {
		if data[i] == '\\' && i+1 < len(data) {
			i += 2
			continue
		}
		if data[i] == quote {
			return i + 1
		}
		i++
	}
	return len(data)
}

func skipLineComment(data []byte, i int) int {
	for i < len(data) && data[i] != '\n' {
		i++
	}
	return i
}

func skipLongComment(data []byte, i int) (int, bool) {
	if i+2 >= len(data) || data[i] != '-' || data[i+1] != '-' {
		return i, false
	}
	return skipLongBracket(data, i+2)
}

func skipLongBracket(data []byte, i int) (int, bool) {
	eqCount, ok := matchLongBracketStart(data, i)
	if !ok {
		return i, false
	}

	i += 2 + eqCount
	for i < len(data) {
		if data[i] == ']' && matchLongBracketEnd(data, i, eqCount) {
			return i + 2 + eqCount, true
		}
		i++
	}
	return len(data), false
}

func matchLongBracketStart(data []byte, i int) (int, bool) {
	if i >= len(data) || data[i] != '[' {
		return 0, false
	}
	eqCount := 0
	j := i + 1
	for j < len(data) && data[j] == '=' {
		eqCount++
		j++
	}
	if j < len(data) && data[j] == '[' {
		return eqCount, true
	}
	return 0, false
}

func matchLongBracketEnd(data []byte, i int, eqCount int) bool {
	if i >= len(data) || data[i] != ']' {
		return false
	}
	j := i + 1
	for k := 0; k < eqCount; k++ {
		if j >= len(data) || data[j] != '=' {
			return false
		}
		j++
	}
	return j < len(data) && data[j] == ']'
}

func findMatchingBrace(data []byte, open int) (int, bool) {
	depth := 0
	for i := open; i < len(data); {
		if next, skipped := skipNonCode(data, i); skipped {
			i = next
			continue
		}

		switch data[i] {
		case '{':
			depth++
		case '}':
			depth--
			if depth == 0 {
				return i, true
			}
			if depth < 0 {
				return -1, false
			}
		}

		i++
	}

	return -1, false
}
