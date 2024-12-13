#! /bin/python
import time
import asyncio
import requests
import pathlib

TMP_FILE = "./out.jmx"
RESULTS_DIR = "./results/"
SLEEP_TIME_SEC = 30


def main():
    tests = create_tests()
    asyncio.run(perform_tests(tests))


def create_tests():
    tests = []

    values = [
        ("all-random", ALL_RANDOM),
        ("path-random", PATH_RANDOM),
        ("same-values", SAME_VALUES)]

    for (server, port) in [("localhost", 3000)]:
        for (rate, loops) in [(1000, 200), (200, 1000)]:
            for (name, value) in values:
                tests.append(
                    {"command": "clear", "server": server, "port": port})
                for count in [1]:
                    tests.append({
                        "command":
                            "test",
                        "name":
                            f"./new-{server}:{port}-{name}-r{rate}-l{loops}-{count}.csv",
                        "test":
                            test(
                                thread_count=rate,
                                throughput_limit=334,
                                loops=loops,
                                server=server,
                                port=port,
                                path="/log",
                                data=value
                            )
                    })

    # CLEAR
    tests.append({"command": "clear", "server": server, "port": port})
    return tests


def clear_db(server, port):
    requests.delete(f"http://{server}:{port}/cleardb")


async def perform_tests(tests):
    pathlib.Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)
    for obj in tests:
        match (obj["command"]):
            case "clear":
                print("--# CLEARING DATABASE #--")
                clear_db(obj["server"], obj["port"])
            case "test":
                print(f"--# RUNNING TEST {obj["name"]} #--")
                await perform_test(obj["test"], obj["name"])
        time.sleep(SLEEP_TIME_SEC)
    pathlib.Path(TMP_FILE).unlink()


async def perform_test(jmx_string, out_file):
    with open(TMP_FILE, "w+") as f:
        f.write(jmx_string)
    process = await asyncio.create_subprocess_shell(
        f"jmeter -n -t {TMP_FILE} -l {RESULTS_DIR}{out_file}"
    )

    await process.wait()


def test(thread_count, loops, throughput_limit, server, port, path, data):
    return TEST_PLAN(
        thread_count=thread_count,
        loops=loops,
        throughput_limit=throughput_limit,
        http=HTTP_REQUEST(
            server=server,
            port=port,
            path=path,
            data=data
        )
    )


ALL_RANDOM = """
<stringProp name="Argument.value">{&#xd;
    &quot;score&quot;:${__Random(0, 100)},&#xd;
    &quot;statusCode&quot;: 10000,&#xd;
    &quot;errorMessage&quot;: &quot;${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;,&#xd;
    &quot;browserName&quot;: &quot;${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;,&#xd;
    &quot;browserVersion&quot;: &quot;${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;,&#xd;
    &quot;pluginName&quot;: &quot;${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;,&#xd;
    &quot;pluginVersion&quot;: &quot;${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;,&#xd;
    &quot;extensionVersion&quot;: &quot;${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;,&#xd;
    &quot;url&quot;: &quot;http://${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}.com&quot;,&#xd;
    &quot;path&quot;: &quot;/${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/)}&quot;&#xd;
}</stringProp>
"""

PATH_RANDOM = """
<stringProp name="Argument.value">{&#xd;
    &quot;score&quot;:50,&#xd;
    &quot;statusCode&quot;: 10000,&#xd;
    &quot;errorMessage&quot;: &quot;It&apos;s a test&quot;,&#xd;
    &quot;browserName&quot;: &quot;A very good browser&quot;,&#xd;
    &quot;browserVersion&quot;: &quot;1.0.0.1&quot;,&#xd;
    &quot;pluginName&quot;: &quot;Test Plugin&quot;,&#xd;
    &quot;pluginVersion&quot;: &quot;1.0&quot;,&#xd;
    &quot;extensionVersion&quot;: &quot;2.0&quot;,&#xd;
    &quot;url&quot;: &quot;http://${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}.org&quot;,&#xd;
    &quot;path&quot;: &quot;/${__RandomString(${__Random(10, 70)}, abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVWXYZ)}&quot;&#xd;
}</stringProp>
"""

SAME_VALUES = """
<stringProp name="Argument.value">{&#xd;
    &quot;score&quot;:50,&#xd;
    &quot;statusCode&quot;: 10000,&#xd;
    &quot;errorMessage&quot;: &quot;It&apos;s a test&quot;,&#xd;
    &quot;browserName&quot;: &quot;A very good browser&quot;,&#xd;
    &quot;browserVersion&quot;: &quot;1.0.0.1&quot;,&#xd;
    &quot;pluginName&quot;: &quot;Test Plugin&quot;,&#xd;
    &quot;pluginVersion&quot;: &quot;1.0&quot;,&#xd;
    &quot;extensionVersion&quot;: &quot;2.0&quot;,&#xd;
    &quot;url&quot;: &quot;http://example.org&quot;,&#xd;
    &quot;path&quot;: &quot;/&quot;&#xd;
}</stringProp>
"""


def HTTP_REQUEST(server, port, path, data):
    return f"""
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Same Log" enabled="true">
    <stringProp name="HTTPSampler.domain">{server}</stringProp>
    <stringProp name="HTTPSampler.port">{port}</stringProp>
    <stringProp name="HTTPSampler.path">{path}</stringProp>
    <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
    <stringProp name="HTTPSampler.method">POST</stringProp>
    <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
    <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
    <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
    <collectionProp name="Arguments.arguments">
        <elementProp name="" elementType="HTTPArgument">
        <boolProp name="HTTPArgument.always_encode">false</boolProp>
        {data}
        <stringProp name="Argument.metadata">=</stringProp>
        </elementProp>
    </collectionProp>
    </elementProp>
</HTTPSamplerProxy>
<hashTree>
    <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="HTTP Header Manager" enabled="true">
    <collectionProp name="HeaderManager.headers">
        <elementProp name="" elementType="Header">
        <stringProp name="Header.name">Content-Type</stringProp>
        <stringProp name="Header.value">application/json</stringProp>
        </elementProp>
    </collectionProp>
    </HeaderManager>
    <hashTree/>
</hashTree>
"""


def TEST_PLAN(thread_count, loops, throughput_limit, http):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
<hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan">
    <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
        <collectionProp name="Arguments.arguments"/>
    </elementProp>
    </TestPlan>
    <hashTree>
    <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group">
        <intProp name="ThreadGroup.num_threads">{thread_count}</intProp>
        <intProp name="ThreadGroup.ramp_time">1</intProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller">
        <stringProp name="LoopController.loops">{loops}</stringProp>
        <boolProp name="LoopController.continue_forever">false</boolProp>
        </elementProp>
    </ThreadGroup>
    <hashTree>
        {http}
        <ConstantThroughputTimer guiclass="TestBeanGUI" testclass="ConstantThroughputTimer" testname="Constant Throughput Timer">
        <intProp name="calcMode">0</intProp>
        <doubleProp>
            <name>throughput</name>
            <value>{throughput_limit * 60}</value>
            <savedValue>0.0</savedValue>
        </doubleProp>
        </ConstantThroughputTimer>
        <hashTree/>
    </hashTree>
    </hashTree>
</hashTree>
</jmeterTestPlan>
"""


if __name__ == "__main__":
    main()
