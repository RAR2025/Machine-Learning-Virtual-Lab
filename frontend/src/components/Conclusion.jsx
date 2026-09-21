import { experimentInfo } from "../data/experimentData";

export default function Conclusion() {
    return (
        <section>
            <h2>Conclusion</h2>
            <p>{experimentInfo.conclusion}</p>
        </section>
    );
}
