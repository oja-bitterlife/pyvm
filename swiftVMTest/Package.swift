// swift-tools-version: 6.3
import PackageDescription

let package = Package(
    name: "swiftVMTestHarness",
    products: [
        .executable(name: "swiftVMTestHarness", targets: ["swiftVMTestHarness"]),
    ],
    dependencies: [
        .package(path: "../swiftVM"),
    ],
    targets: [
        .executableTarget(
            name: "swiftVMTestHarness",
            dependencies: [
                .product(name: "swiftVMLib", package: "swiftVM"),
            ],
            path: "Sources"
        ),
    ]
)
